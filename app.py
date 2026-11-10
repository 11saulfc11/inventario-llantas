import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Archivos de base de datos local
USUARIOS_FILE = "usuarios.xlsx"
INVENTARIO_FILE = "inventario_general.xlsx"
VENTAS_FILE = "ventas_realizadas.xlsx"

# ---------------------------------------------------------
# FUNCIONES DE CARGA Y PERSISTENCIA EXCEL
# ---------------------------------------------------------
def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        df = pd.DataFrame(columns=["Usuario", "Password"])
        df.to_excel(USUARIOS_FILE, index=False)
        return df
    return pd.read_excel(USUARIOS_FILE)

def registrar_usuario(usuario, password):
    df = cargar_usuarios()
    if usuario in df["Usuario"].values:
        return False
    nuevo_usuario = pd.DataFrame([{"Usuario": usuario, "Password": str(password)}])
    df = pd.concat([df, nuevo_usuario], ignore_index=True)
    df.to_excel(USUARIOS_FILE, index=False)
    return True

def validar_login(usuario, password):
    df = cargar_usuarios()
    df["Password"] = df["Password"].astype(str)
    user_match = df[(df["Usuario"] == usuario) & (df["Password"] == str(password))]
    return not user_match.empty

def cargar_inventario():
    if not os.path.exists(INVENTARIO_FILE):
        df = pd.DataFrame(columns=["Código", "Descripción", "Proveedor", "Cantidad", "Precio Unitario", "Precio con IVA"])
        df.to_excel(INVENTARIO_FILE, index=False)
        return df
    df = pd.read_excel(INVENTARIO_FILE)
    # Asegurar compatibilidad si el archivo antiguo no tiene la columna Proveedor
    if "Proveedor" not in df.columns:
        df["Proveedor"] = "General"
    return df

def guardar_inventario(df):
    df.to_excel(INVENTARIO_FILE, index=False)

def cargar_ventas():
    if not os.path.exists(VENTAS_FILE):
        df = pd.DataFrame(columns=["Fecha", "Cliente", "Código Llanta", "Descripción", "Cantidad", "Total Pagado", "Vendedor"])
        df.to_excel(VENTAS_FILE, index=False)
        return df
    return pd.read_excel(VENTAS_FILE)

def guardar_venta(df):
    df.to_excel(VENTAS_FILE, index=False)

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Sistema de Inventario de Llantas", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

# ---------------------------------------------------------
# PANTALLA DE ACCESO (LOGIN / REGISTRO)
# ---------------------------------------------------------
if not st.session_state["autenticado"]:
    st.title("🔑 Sistema de Acceso - Inventario")
    
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
        st.subheader("Ingresar al Sistema")
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
        if st.button("Iniciar Sesión"):
            if validar_login(user_input, pass_input):
                st.session_state["autenticado"] = True
                st.session_state["usuario_actual"] = user_input
                st.success(f"¡Bienvenido, {user_input}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
                
    with tab_registro:
        st.subheader("Crear Cuenta Nueva")
        new_user = st.text_input("Nuevo Usuario", key="reg_user")
        new_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirmar Contraseña", type="password", key="reg_confirm_pass")
        
        if st.button("Crear Cuenta"):
            if not new_user or not new_pass:
                st.warning("Por favor completa todos los campos.")
            elif new_pass != confirm_pass:
                st.error("Las contraseñas no coinciden.")
            else:
                if registrar_usuario(new_user, new_pass):
                    st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                else:
                    st.error("El nombre de usuario ya existe.")

# ---------------------------------------------------------
# APLICACIÓN PRINCIPAL (UNA VEZ AUTENTICADO)
# ---------------------------------------------------------
else:
    # --- BARRA LATERAL (LOGOTIPO Y USUARIO) ---
    st.sidebar.title("🛞 Control de Llantas")
    
    # Subir o mostrar logotipo en la parte superior del menú lateral
    st.sidebar.markdown("### Logotipo del Negocio")
    logo_file = st.sidebar.file_uploader("Sube tu logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if logo_file is not None:
        st.sidebar.image(logo_file, use_container_width=True)
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 **Usuario activo:** {st.session_state['usuario_actual']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.session_state["usuario_actual"] = ""
        st.rerun()

    # --- PESTAÑAS PRINCIPALES DEL SISTEMA ---
    menu_principal = st.tabs(["📦 Inventario", "➕ Agregar Producto", "✏️ Modificar Inventario", "💰 Registrar Venta", "📋 Historial de Ventas"])
    
    df_inv = cargar_inventario()
    df_ventas = cargar_ventas()

    # 1. PESTAÑA: VER INVENTARIO
    with menu_principal[0]:
        st.subheader("📋 Inventario General Actual")
        if not df_inv.empty:
            st.dataframe(df_inv, use_container_width=True)
        else:
            st.info("No hay productos registrados en el inventario.")

    # 2. PESTAÑA: AGREGAR PRODUCTO
    with menu_principal[1]:
        st.subheader("➕ Agregar Nueva Llanta")
        with st.form("form_agregar"):
            col1, col2 = st.columns(2)
            with col1:
                codigo = st.text_input("Código / Medida de Llanta")
                descripcion = st.text_input("Descripción (Marca / Modelo)")
                proveedor = st.text_input("Proveedor (¿Quién la trajo?)")
            with col2:
                cantidad = st.number_input("Cantidad en Existencia", min_value=0, step=1)
                precio_u = st.number_input("Precio Unitario ($)", min_value=0.0, step=0.5, format="%.2f")
                calcular_iva = st.checkbox("Incluir IVA (16%)", value=True)
                
            btn_guardar = st.form_submit_button("Guardar en Inventario")
            
            if btn_guardar:
                if not codigo:
                    st.warning("El código es obligatorio.")
                else:
                    precio_iva = precio_u * 1.16 if calcular_iva else precio_u
                    nuevo_item = {
                        "Código": codigo,
                        "Descripción": descripcion,
                        "Proveedor": proveedor,
                        "Cantidad": cantidad,
                        "Precio Unitario": precio_u,
                        "Precio con IVA": round(precio_iva, 2)
                    }
                    df_inv = pd.concat([df_inv, pd.DataFrame([nuevo_item])], ignore_index=True)
                    guardar_inventario(df_inv)
                    st.success("¡Producto agregado y guardado en Excel correctamente!")
                    st.rerun()

    # 3. PESTAÑA: MODIFICAR INVENTARIO
    with menu_principal[2]:
        st.subheader("✏️ Modificar o Eliminar Producto Existente")
        if not df_inv.empty:
            codigo_a_editar = st.selectbox("Selecciona el código del producto a modificar", df_inv["Código"].unique())
            
            # Buscar datos actuales del producto
            prod_actual = df_inv[df_inv["Código"] == codigo_a_editar].iloc[0]
            
            with st.form("form_editar"):
                nuevo_desc = st.text_input("Descripción", value=str(prod_actual["Descripción"]))
                nuevo_prov = st.text_input("Proveedor", value=str(prod_actual["Proveedor"]))
                nueva_cant = st.number_input("Cantidad", min_value=0, value=int(prod_actual["Cantidad"]), step=1)
                nuevo_precio = st.number_input("Precio Unitario ($)", min_value=0.0, value=float(prod_actual["Precio Unitario"]), step=0.5, format="%.2f")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    btn_actualizar = st.form_submit_button("Actualizar Producto")
                with col_btn2:
                    btn_eliminar = st.form_submit_button("🗑️ Eliminar Producto")
                
                if btn_actualizar:
                    df_inv.loc[df_inv["Código"] == codigo_a_editar, "Descripción"] = nuevo_desc
                    df_inv.loc[df_inv["Código"] == codigo_a_editar, "Proveedor"] = nuevo_prov
                    df_inv.loc[df_inv["Código"] == codigo_a_editar, "Cantidad"] = nueva_cant
                    df_inv.loc[df_inv["Código"] == codigo_a_editar, "Precio Unitario"] = nuevo_precio
                    df_inv.loc[df_inv["Código"] == codigo_a_editar, "Precio con IVA"] = round(nuevo_precio * 1.16, 2)
                    
                    guardar_inventario(df_inv)
                    st.success(f"Producto {codigo_a_editar} actualizado con éxito.")
                    st.rerun()
                    
                if btn_eliminar:
                    df_inv = df_inv[df_inv["Código"] != codigo_a_editar]
                    guardar_inventario(df_inv)
                    st.warning(f"Producto {codigo_a_editar} eliminado del inventario.")
                    st.rerun()
        else:
            st.info("No hay productos para modificar.")

    # 4. PESTAÑA: REGISTRAR VENTA
    with menu_principal[3]:
        st.subheader("💰 Registrar Salida / Venta a Cliente")
        if not df_inv.empty:
            with st.form("form_venta"):
                cliente = st.text_input("Nombre del Cliente (¿A quién se le vendió?)")
                codigo_venta = st.selectbox("Selecciona la Llanta Vendida", df_inv["Código"].unique())
                
                # Obtener stock actual
                stock_disponible = int(df_inv.loc[df_inv["Código"] == codigo_venta, "Cantidad"].values[0])
                precio_venta = float(df_inv.loc[df_inv["Código"] == codigo_venta, "Precio con IVA"].values[0])
                desc_venta = str(df_inv.loc[df_inv["Código"] == codigo_venta, "Descripción"].values[0])
                
                st.write(f"Stock disponible: **{stock_disponible}** | Precio unitario con IVA: **${precio_venta:.2f}**")
                
                cant_a_vender = st.number_input("Cantidad a vender", min_value=1, max_value=max(1, stock_disponible), step=1)
                
                btn_registrar_venta = st.form_submit_button("Confirmar Venta")
                
                if btn_registrar_venta:
                    if not cliente:
                        st.warning("Debes escribir el nombre del cliente.")
                    elif cant_a_vender > stock_disponible:
                        st.error("No hay suficiente stock para esta venta.")
                    else:
                        # Descontar del inventario
                        df_inv.loc[df_inv["Código"] == codigo_venta, "Cantidad"] = stock_disponible - cant_a_vender
                        guardar_inventario(df_inv)
                        
                        # Registrar la venta
                        nueva_venta = {
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Cliente": cliente,
                            "Código Llanta": codigo_venta,
                            "Descripción": desc_venta,
                            "Cantidad": cant_a_vender,
                            "Total Pagado": round(cant_a_vender * precio_venta, 2),
                            "Vendedor": st.session_state["usuario_actual"]
                        }
                        df_ventas = pd.concat([df_ventas, pd.DataFrame([nueva_venta])], ignore_index=True)
                        guardar_venta(df_ventas)
                        
                        st.success(f"¡Venta registrada con éxito a {cliente}! Inventario actualizado.")
                        st.rerun()
        else:
            st.info("No hay inventario disponible para realizar ventas.")

    # 5. PESTAÑA: HISTORIAL DE VENTAS
    with menu_principal[4]:
        st.subheader("📋 Historial de Ventas (A quién se le vendió)")
        if not df_ventas.empty:
            st.dataframe(df_ventas, use_container_width=True)
        else:
            st.info("Aún no se ha registrado ninguna venta.")
