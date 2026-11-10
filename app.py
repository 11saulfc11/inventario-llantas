import streamlit as st
import pandas as pd
import os

# Archivos de base de datos local
USUARIOS_FILE = "usuarios.xlsx"
INVENTARIO_FILE = "inventario_general.xlsx"

# ---------------------------------------------------------
# FUNCIONES AUXILIARES PARA MANEJO DE ARCHIVOS EXCEL
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
        df = pd.DataFrame(columns=["Código", "Descripción", "Cantidad", "Precio Unitario", "Precio con IVA"])
        df.to_excel(INVENTARIO_FILE, index=False)
        return df
    return pd.read_excel(INVENTARIO_FILE)

def guardar_inventario(df):
    df.to_excel(INVENTARIO_FILE, index=False)

# ---------------------------------------------------------
# CONFIGURACIÓN Y ESTADO DE SESIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="Sistema de Inventario de Llantas", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

# ---------------------------------------------------------
# INTERFAZ DE AUTENTICACIÓN (LOGIN Y REGISTRO)
# ---------------------------------------------------------
if not st.session_state["autenticado"]:
    st.title("🔑 Sistema de Acceso - Inventario")
    
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
        st.subheader("Ingreso de Usuarios")
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
        if st.button("Iniciar Sesión"):
            if validar_login(user_input, pass_input):
                st.session_state["autenticado"] = True
                st.session_state["usuario_actual"] = user_input
                st.success(f"Bienvenido, {user_input}!")
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
                    st.success("¡Cuenta creada con éxito! Ahora puedes iniciar sesión.")
                else:
                    st.error("El nombre de usuario ya existe. Elige otro.")

# ---------------------------------------------------------
# INTERFAZ PRINCIPAL DEL INVENTARIO
# ---------------------------------------------------------
else:
    st.sidebar.title(f"👤 Usuario: {st.session_state['usuario_actual']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.session_state["usuario_actual"] = ""
        st.rerun()
        
    st.title("🛞 Gestión de Inventario de Llantas")
    
    df_inv = cargar_inventario()
    
    # Formulario para agregar producto
    with st.expander("➕ Agregar nuevo producto al inventario", expanded=False):
        with st.form("form_agregar"):
            col1, col2 = st.columns(2)
            with col1:
                codigo = st.text_input("Código / Medida de Llanta")
                descripcion = st.text_input("Descripción (Marca / Modelo)")
                cantidad = st.number_input("Cantidad en Existencia", min_value=0, step=1)
            with col2:
                precio_u = st.number_input("Precio Unitario ($)", min_value=0.0, step=0.5, format="%.2f")
                calcular_iva = st.checkbox("Incluir IVA (16%)", value=True)
                
            btn_guardar = st.form_submit_button("Guardar Producto")
            
            if btn_guardar:
                if not codigo:
                    st.warning("El campo de Código es obligatorio.")
                else:
                    precio_iva = precio_u * 1.16 if calcular_iva else precio_u
                    nuevo_item = {
                        "Código": codigo,
                        "Descripción": descripcion,
                        "Cantidad": cantidad,
                        "Precio Unitario": precio_u,
                        "Precio con IVA": round(precio_iva, 2)
                    }
                    df_inv = pd.concat([df_inv, pd.DataFrame([nuevo_item])], ignore_index=True)
                    guardar_inventario(df_inv)
                    st.success("Producto guardado correctamente en Excel.")
                    st.rerun()
                    
    # Mostrar y editar inventario
    st.subheader("📋 Inventario Actual")
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True)
        
        # Eliminar registro
        with st.expander("🗑️ Eliminar Producto"):
            codigo_eliminar = st.selectbox("Selecciona el código a eliminar", df_inv["Código"].unique())
            if st.button("Eliminar"):
                df_inv = df_inv[df_inv["Código"] != codigo_eliminar]
                guardar_inventario(df_inv)
                st.success(f"Producto {codigo_eliminar} eliminado.")
                st.rerun()
    else:
        st.info("El inventario está vacío. Agrega un producto arriba.")

  
