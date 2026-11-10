import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Archivos de base de datos local
USUARIOS_FILE = "usuarios.xlsx"
INVENTARIO_FILE = "inventario_general.xlsx"
VENTAS_FILE = "ventas_realizadas.xlsx"
EXTERNOS_FILE = "inventarios_externos.xlsx"

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
        df = pd.DataFrame(columns=["Usuario", "Fecha Adquisición", "Medida", "Descripción", "Proveedor", "Cantidad", "Precio Unitario", "Precio con IVA"])
        df.to_excel(INVENTARIO_FILE, index=False)
        return df
    return pd.read_excel(INVENTARIO_FILE)

def guardar_inventario(df):
    df.to_excel(INVENTARIO_FILE, index=False)

def cargar_ventas():
    if not os.path.exists(VENTAS_FILE):
        df = pd.DataFrame(columns=["Usuario", "Fecha Venta", "Cliente", "Medida Llanta", "Descripción", "Cantidad", "Precio Venta", "Total Pagado", "Tipo Pago", "Fecha Vencimiento Crédito", "Estado Crédito"])
        df.to_excel(VENTAS_FILE, index=False)
        return df
    return pd.read_excel(VENTAS_FILE)

def guardar_venta(df):
    df.to_excel(VENTAS_FILE, index=False)

def cargar_externos():
    if not os.path.exists(EXTERNOS_FILE):
        df = pd.DataFrame(columns=["Usuario", "Negocio / Proveedor Externo", "Medida", "Descripción", "Cantidad", "Precio"])
        df.to_excel(EXTERNOS_FILE, index=False)
        return df
    return pd.read_excel(EXTERNOS_FILE)

def guardar_externos(df):
    df.to_excel(EXTERNOS_FILE, index=False)

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Control de Inventario de Llantas", page_icon="🛞", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

# ---------------------------------------------------------
# PANTALLA DE ACCESO (LOGIN / REGISTRO)
# ---------------------------------------------------------
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🛞 Control de Llantas</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: gray;'>Sistema de Gestión Privado</h3>", unsafe_allow_html=True)
        
        tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
        
        with tab_login:
            st.write("")
            user_input = st.text_input("Usuario", key="login_user")
            pass_input = st.text_input("Contraseña", type="password", key="login_pass")
            st.write("")
            if st.button("Ingresar al Sistema", use_container_width=True):
                if validar_login(user_input, pass_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = user_input
                    st.success(f"¡Bienvenido, {user_input}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
        with tab_registro:
            st.write("")
            new_user = st.text_input("Nuevo Usuario", key="reg_user")
            new_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirmar Contraseña", type="password", key="reg_confirm_pass")
            st.write("")
            if st.button("Crear Cuenta", use_container_width=True):
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
# APLICACIÓN PRINCIPAL (PRIVADA POR USUARIO)
# ---------------------------------------------------------
else:
    usuario_actual = st.session_state["usuario_actual"]
    
    # --- BARRA LATERAL ESTILIZADA ---
    st.sidebar.markdown(f"## 🛞 Menú Principal")
    logo_file = st.sidebar.file_uploader("🖼️ Sube tu Logotipo", type=["png", "jpg", "jpeg"])
    if logo_file is not None:
        st.sidebar.image(logo_file, use_container_width=True)
        st.session_state["logo_img"] = logo_file
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **Usuario activo:** `{usuario_actual}`")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario_actual"] = ""
        st.rerun()

    # Cargar datos globales y filtrar por usuario
    df_inv_total = cargar_inventario()
    df_ventas_total = cargar_ventas()
    df_ext_total = cargar_externos()

    for col in ["Usuario", "Fecha Adquisición", "Medida", "Descripción", "Proveedor", "Cantidad", "Precio Unitario", "Precio con IVA"]:
        if col not in df_inv_total.columns:
            df_inv_total[col] = ""
            
    for col in ["Usuario", "Fecha Venta", "Cliente", "Medida Llanta", "Descripción", "Cantidad", "Precio Venta", "Total Pagado", "Tipo Pago", "Fecha Vencimiento Crédito", "Estado Crédito"]:
        if col not in df_ventas_total.columns:
            df_ventas_total[col] = ""

    for col in ["Usuario", "Negocio / Proveedor Externo", "Medida", "Descripción", "Cantidad", "Precio"]:
        if col not in df_ext_total.columns:
            df_ext_total[col] = ""

    df_inv = df_inv_total[df_inv_total["Usuario"] == usuario_actual].copy()
    df_ventas = df_ventas_total[df_ventas_total["Usuario"] == usuario_actual].copy()
    df_ext = df_ext_total[df_ext_total["Usuario"] == usuario_actual].copy()

    # --- ALERTAS DE CRÉDITO EN BARRA LATERAL ---
    if not df_ventas.empty:
        hoy = datetime.now().date()
        creditos_pendientes = df_ventas[(df_ventas["Tipo Pago"] == "Crédito") & (df_ventas["Estado Crédito"] == "Pendiente")]
        for idx, row in creditos_pendientes.iterrows():
            if pd.notna(row["Fecha Vencimiento Crédito"]) and str(row["Fecha Vencimiento Crédito"]) != "":
                try:
                    f_venc = datetime.strptime(str(row["Fecha Vencimiento Crédito"])[:10], "%Y-%m-%d").date()
                    dias_restantes = (f_venc - hoy).days
                    if dias_restantes < 0:
                        st.sidebar.error(f"⚠️ **Crédito Vencido**: {row['Cliente']} (${row['Total Pagado']})")
                    elif dias_restantes <= 3:
                        st.sidebar.warning(f"⏰ **Vence en {dias_restantes}d**: {row['Cliente']}")
                except:
                    pass

    # --- PESTAÑAS PRINCIPALES ---
    menu_principal = st.tabs(["📦 Mi Inventario", "➕ Agregar", "✏️ Modificar", "💰 Vender", "🌐 Inventarios Externos", "🔍 Buscador Global", "🖨️ Imprimir Nota", "📋 Historial"])

    # 1. MI INVENTARIO
    with menu_principal[0]:
        st.markdown("### 📋 Resumen de tu Inventario Actual")
        if not df_inv.empty:
            total_llantas = int(df_inv["Cantidad"].sum())
            total_modelos = len(df_inv)
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("📦 Total de Llantas en Stock", total_llantas)
            col_m2.metric("🏷️ Medidas Registradas", total_modelos)
            st.markdown("---")
            st.dataframe(df_inv.drop(columns=["Usuario"]), use_container_width=True)
        else:
            st.info("Aún no tienes llantas registradas. Ve a la pestaña **Agregar** para empezar.")

    # 2. AGREGAR LLANTA
    with menu_principal[1]:
        st.markdown("### ➕ Registrar Nueva Entrada de Llantas")
        with st.form("form_agregar", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                fecha_adq = st.date_input("📅 Fecha de Adquisición", value=datetime.now())
                medida = st.text_input("🛞 Medida de la Llanta (Ej. 175/70R13)")
                descripcion = st.text_input("📝 Descripción (Marca / Modelo)")
            with col2:
                proveedor = st.text_input("🏭 Proveedor (¿Quién la trajo?)")
                cantidad = st.number_input("🔢 Cantidad en Existencia", min_value=1, step=1)
                precio_u = st.number_input("💲 Precio Unitario Base ($)", min_value=0.0, step=0.5, format="%.2f")
                calcular_iva = st.checkbox("Incluir IVA Automático (16%)", value=True)
                
            st.write("")
            btn_guardar = st.form_submit_button("💾 Guardar en mi Inventario", use_container_width=True)
            
            if btn_guardar:
                if not medida:
                    st.warning("La medida de la llanta es obligatoria.")
                else:
                    precio_iva = precio_u * 1.16 if calcular_iva else precio_u
                    nuevo_item = {
                        "Usuario": usuario_actual,
                        "Fecha Adquisición": str(fecha_adq),
                        "Medida": medida,
                        "Descripción": descripcion,
                        "Proveedor": proveedor,
                        "Cantidad": cantidad,
                        "Precio Unitario": precio_u,
                        "Precio con IVA": round(precio_iva, 2)
                    }
                    df_inv_total = pd.concat([df_inv_total, pd.DataFrame([nuevo_item])], ignore_index=True)
                    guardar_inventario(df_inv_total)
                    st.success("¡Llanta agregada correctamente a tu inventario!")

    # 3. MODIFICAR INVENTARIO
    with menu_principal[2]:
        st.markdown("### ✏️ Modificar o Eliminar una Llanta")
        if not df_inv.empty:
            medida_a_editar = st.selectbox("Selecciona la Medida a gestionar", df_inv["Medida"].unique())
            prod_actual = df_inv[df_inv["Medida"] == medida_a_editar].iloc[0]
            
            with st.form("form_editar"):
                nueva_desc = st.text_input("Descripción", value=str(prod_actual["Descripción"]))
                nuevo_prov = st.text_input("Proveedor", value=str(prod_actual["Proveedor"]))
                nueva_cant = st.number_input("Cantidad", min_value=0, value=int(prod_actual["Cantidad"]), step=1)
                nuevo_precio = st.number_input("Precio Unitario ($)", min_value=0.0, value=float(prod_actual["Precio Unitario"]), step=0.5, format="%.2f")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    btn_actualizar = st.form_submit_button("🔄 Actualizar Datos", use_container_width=True)
                with col_btn2:
                    btn_eliminar = st.form_submit_button("🗑️ Eliminar Llanta", use_container_width=True)
                
                if btn_actualizar:
                    df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_a_editar), "Descripción"] = nueva_desc
                    df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_a_editar), "Proveedor"] = nuevo_prov
                    df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_a_editar), "Cantidad"] = nueva_cant
                    df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_a_editar), "Precio Unitario"] = nuevo_precio
                    df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_a_editar), "Precio con IVA"] = round(nuevo_precio * 1.16, 2)
                    
                    guardar_inventario(df_inv_total)
                    st.success("Inventario actualizado con éxito.")
                    st.rerun()
                    
                if btn_eliminar:
                    df_inv_total = df_inv_total[~((df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_a_editar))]
                    guardar_inventario(df_inv_total)
                    st.warning("Llanta eliminada de tu inventario.")
                    st.rerun()
        else:
            st.info("No tienes productos en tu inventario para modificar.")

    # 4. REGISTRAR VENTA
    with menu_principal[3]:
        st.markdown("### 💰 Registrar Venta o Salida de Producto")
        if not df_inv.empty:
            with st.form("form_venta", clear_on_submit=True):
                cliente = st.text_input("👤 Nombre del Cliente")
                medida_venta = st.selectbox("🛞 Selecciona la Medida de la Llanta", df_inv["Medida"].unique())
                
                stock_disponible = int(df_inv.loc[df_inv["Medida"] == medida_venta, "Cantidad"].values[0])
                precio_sugerido = float(df_inv.loc[df_inv["Medida"] == medida_venta, "Precio con IVA"].values[0])
                desc_venta = str(df_inv.loc[df_inv["Medida"] == medida_venta, "Descripción"].values[0])
                
                st.info(f"Stock disponible: **{stock_disponible} unidades** | Precio sugerido con IVA: **${precio_sugerido:.2f}**")
                
                cant_a_vender = st.number_input("Cantidad a vender", min_value=1, max_value=max(1, stock_disponible), step=1)
                precio_personalizado = st.number_input("Precio de venta unitario ($)", min_value=0.0, value=precio_sugerido, step=0.5, format="%.2f")
                
                tipo_pago = st.selectbox("Tipo de Pago", ["Contado", "Crédito"])
                
                fecha_vencimiento = ""
                if tipo_pago == "Crédito":
                    fecha_vencimiento = st.date_input("📅 Fecha límite de pago (Vencimiento del Crédito)", value=datetime.now() + timedelta(days=30))
                
                st.write("")
                btn_registrar_venta = st.form_submit_button("🚀 Confirmar y Registrar Venta", use_container_width=True)
                
                if btn_registrar_venta:
                    if not cliente:
                        st.warning("Debes escribir el nombre del cliente.")
                    elif cant_a_vender > stock_disponible:
                        st.error("No hay suficiente stock disponible para esta venta.")
                    else:
                        stock_actual_real = int(df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_venta), "Cantidad"].values[0])
                        df_inv_total.loc[(df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_venta), "Cantidad"] = stock_actual_real - cant_a_vender
                        guardar_inventario(df_inv_total)
                        
                        nueva_venta = {
                            "Usuario": usuario_actual,
                            "Fecha Venta": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Cliente": cliente,
                            "Medida Llanta": medida_venta,
                            "Descripción": desc_venta,
                            "Cantidad": cant_a_vender,
                            "Precio Venta": precio_personalizado,
                            "Total Pagado": round(cant_a_vender * precio_personalizado, 2),
                            "Tipo Pago": tipo_pago,
                            "Fecha Vencimiento Crédito": str(fecha_vencimiento) if tipo_pago == "Crédito" else "N/A",
                            "Estado Crédito": "Pendiente" if tipo_pago == "Crédito" else "Pagado"
                        }
                        df_ventas_total = pd.concat([df_ventas_total, pd.DataFrame([nueva_venta])], ignore_index=True)
                        guardar_venta(df_ventas_total)
                        
                        st.success(f"¡Venta registrada con éxito a {cliente}!")
        else:
            st.info("No tienes stock disponible para realizar ventas.")

    # 5. INVENTARIOS EXTERNOS (NUEVO)
    with menu_principal[4]:
        st.markdown("### 🌐 Registrar Inventarios Externos / Otros Proveedores")
        st.write("Agrega aquí las existencias y precios de otros negocios o proveedores externos para poder consultarlos y buscarlos rápidamente.")
        
        with st.form("form_externo", clear_on_submit=True):
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                negocio_ext = st.text_input("🏭 Nombre del Proveedor / Taller Externo")
                medida_ext = st.text_input("🛞 Medida de la Llanta (Ej. 185/65R15)")
            with col_ex2:
                desc_ext = st.text_input("📝 Descripción / Marca")
                cant_ext = st.number_input("🔢 Cantidad Disponible", min_value=1, step=1)
                precio_ext = st.number_input("💲 Precio Externo ($)", min_value=0.0, step=0.5, format="%.2f")
                
            btn_guardar_ext = st.form_submit_button("💾 Guardar Inventario Externo", use_container_width=True)
            if btn_guardar_ext:
                if not medida_ext or not negocio_ext:
                    st.warning("El nombre del negocio y la medida son obligatorios.")
                else:
                    nuevo_ext = {
                        "Usuario": usuario_actual,
                        "Negocio / Proveedor Externo": negocio_ext,
                        "Medida": medida_ext,
                        "Descripción": desc_ext,
                        "Cantidad": cant_ext,
                        "Precio": precio_ext
                    }
                    df_ext_total = pd.concat([df_ext_total, pd.DataFrame([nuevo_ext])], ignore_index=True)
                    guardar_externos(df_ext_total)
                    st.success("¡Registro externo guardado con éxito!")
        
        st.markdown("---")
        st.markdown("#### 📋 Listado de Inventarios Externos Registrados")
        if not df_ext.empty:
            st.dataframe(df_ext.drop(columns=["Usuario"]), use_container_width=True)
            
            # Opción para eliminar registro externo
            ext_a_borrar = st.selectbox("Selecciona un registro externo para eliminar", df_ext.index.tolist(), format_func=lambda x: f"{df_ext.loc[x, 'Negocio / Proveedor Externo']} - {df_ext.loc[x, 'Medida']}")
            if st.button("🗑️ Eliminar Registro Externo"):
                df_ext_total = df_ext_total.drop(ext_a_borrar)
                guardar_externos(df_ext_total)
                st.warning("Registro externo eliminado.")
                st.rerun()
        else:
            st.info("No hay inventarios externos registrados.")

    # 6. BUSCADOR GLOBAL DE MEDIDAS (NUEVO)
    with menu_principal[5]:
        st.markdown("### 🔍 Buscador Global de Medidas de Llantas")
        st.write("Busca una medida específica y el sistema te mostrará todas las opciones disponibles en tu propio inventario y en los inventarios externos.")
        
        busqueda_medida = st.text_input("Escribe la medida a buscar (ej. 175/70R13 o parte de ella):")
        
        if busqueda_medida:
            # Buscar en inventario propio
            matches_propios = pd.DataFrame()
            if not df_inv.empty:
                matches_propios = df_inv[df_inv["Medida"].str.contains(busqueda_medida, case=False, na=False)].copy()
                matches_propios["Origen"] = f"🏠 Mi Inventario ({usuario_actual})"
                matches_propios["Precio Disponible"] = matches_propios["Precio conIVA"] if "Precio conIVA" in matches_propios.columns else matches_propios["Precio con IVA"]
            
            # Buscar en inventarios externos
            matches_externos = pd.DataFrame()
            if not df_ext.empty:
                matches_externos = df_ext[df_ext["Medida"].str.contains(busqueda_medida, case=False, na=False)].copy()
                matches_externos["Origen"] = matches_externos["Negocio / Proveedor Externo"]
                matches_externos["Precio Disponible"] = matches_externos["Precio"]
            
            st.markdown(f"#### Resultados para la medida: *{busqueda_medida}*")
            
            if not matches_propios.empty or not matches_externos.empty:
                # Mostrar propios
                if not matches_propios.empty:
                    st.markdown("##### 🏠 Opciones en tu Inventario:")
                    st.dataframe(matches_propios[["Medida", "Descripción", "Cantidad", "Precio con IVA", "Proveedor"]], use_container_width=True)
                
                # Mostrar externos
                if not matches_externos.empty:
                    st.markdown("##### 🌐 Opciones en Proveedores / Talleres Externos:")
                    st.dataframe(matches_externos[["Negocio / Proveedor Externo", "Medida", "Descripción", "Cantidad", "Precio"]], use_container_width=True)
            else:
                st.warning("No se encontraron coincidencias para esa medida ni en tu inventario ni en los externos.")
        else:
            st.info("Escribe arriba una medida de llanta para realizar la búsqueda global.")

    # 7. IMPRIMIR NOTA / TICKET (CORREGIDO CON BOTÓN DE IMPRESIÓN JS)
    with menu_principal[6]:
        st.markdown("### 🖨️ Generar y Mandar a Imprimir Nota de Venta")
        if not df_ventas.empty:
            indices_ventas = df_ventas.index.tolist()
            venta_seleccionada = st.selectbox(
                "Selecciona la venta para generar su nota:", 
                indices_ventas, 
                format_func=lambda x: f"Fecha: {df_ventas.loc[x, 'Fecha Venta']} | Cliente: {df_ventas.loc[x, 'Cliente']} | Total: ${df_ventas.loc[x, 'Total Pagado']}"
            )
            
            v_data = df_ventas.loc[venta_seleccionada]
            
            st.markdown("---")
            
            # Botón de impresión directa mediante JavaScript
            st.markdown("""
                <div style="text-align: center; margin-bottom: 20px;">
                    <button onclick="window.print()" style="background-color: #2e7d32; color: white; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; font-weight: bold;">
                        🖨️ Imprimir Ticket / Nota Ahora
                    </button>
                </div>
            """, unsafe_allow_html=True)
            
            # Contenedor con diseño de Ticket Comercial
            col_ticket1, col_ticket2, col_ticket3 = st.columns([1, 2, 1])
            with col_ticket2:
                ticket_container = st.container()
                with ticket_container:
                    st.markdown("<div style='border: 2px solid #ccc; padding: 25px; border-radius: 10px; background-color: white; color: black; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                    
                    if "logo_img" in st.session_state and st.session_state["logo_img"] is not None:
                        st.image(st.session_state["logo_img"], width=120)
                    
                    st.markdown(f"<h3 style='text-align: center; margin: 0;'>NOTA DE VENTA</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; color: gray; margin: 0;'>Control de Llantas - Negocio: <b>{usuario_actual}</b></p>", unsafe_allow_html=True)
                    st.markdown("---")
                    
                    st.write(f"📅 **Fecha:** {v_data['Fecha Venta']}")
                    st.write(f"👤 **Cliente:** {v_data['Cliente']}")
                    st.write(f"💳 **Tipo de Pago:** {v_data['Tipo Pago']}")
                    if v_data['Tipo Pago'] == "Crédito":
                        st.write(f"⏰ **Vencimiento Crédito:** {v_data['Fecha Vencimiento Crédito']}")
                        st.write(f"📌 **Estado:** {v_data['Estado Crédito']}")
                    
                    st.markdown("---")
                    st.markdown("#### Detalle del Producto:")
                    st.write(f"• **Medida:** {v_data['Medida Llanta']}")
                    st.write(f"• **Descripción:** {v_data['Descripción']}")
                    st.write(f"• **Cantidad:** {v_data['Cantidad']} pieza(s)")
                    st.write(f"• **Precio Unitario:** ${v_data['Precio Venta']:,.2f}")
                    
                    st.markdown("---")
                    st.markdown(f"<h3 style='text-align: right;'>Total: ${v_data['Total Pagado']:,.2f}</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; font-size: 12px; color: gray;'>¡Gracias por su preferencia!</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.info("No hay ventas registradas para generar notas.")

    # 8. HISTORIAL Y ADMINISTRACIÓN DE VENTAS
    with menu_principal[7]:
        st.markdown("### 📋 Historial de Ventas, Créditos y Administración")
        if not df_ventas.empty:
            st.dataframe(df_ventas.drop(columns=["Usuario"]), use_container_width=True)
            
            st.markdown("---")
            col_acc1, col_acc2 = st.columns(2)
            
            with col_acc1:
                st.markdown("#### 💳 Marcar Crédito como Pagado")
                creditos_pendientes_lista = df_ventas[(df_ventas["Tipo Pago"] == "Crédito") & (df_ventas["Estado Crédito"] == "Pendiente")]
                if not creditos_pendientes_lista.empty:
                    indices_pendientes = creditos_pendientes_lista.index.tolist()
                    venta_a_saldar = st.selectbox("Selecciona la venta a saldar", indices_pendientes, format_func=lambda x: f"{df_ventas.loc[x, 'Cliente']} - ${df_ventas.loc[x, 'Total Pagado']}")
                    if st.button("Marcar Crédito como Pagado"):
                        df_ventas_total.loc[venta_a_saldar, "Estado Crédito"] = "Pagado"
                        guardar_venta(df_ventas_total)
                        st.success("¡El crédito ha sido marcado como Pagado!")
                        st.rerun()
                else:
                    st.success("No hay créditos pendientes por cobrar 🎉")

            with col_acc2:
                st.markdown("#### 🗑️ Eliminar Registro de Venta")
                if not df_ventas.empty:
                    indices_usuario = df_ventas.index.tolist()
                    venta_a_borrar = st.selectbox("Selecciona la venta a eliminar", indices_usuario, format_func=lambda x: f"{df_ventas.loc[x, 'Fecha Venta']} - {df_ventas.loc[x, 'Cliente']} (${df_ventas.loc[x, 'Total Pagado']})")
                    if st.button("Eliminar Venta Seleccionada", type="primary"):
                        medida_v = df_ventas_total.loc[venta_a_borrar, "Medida Llanta"]
                        cant_v = int(df_ventas_total.loc[venta_a_borrar, "Cantidad"])
                        
                        filtro_inv = (df_inv_total["Usuario"] == usuario_actual) & (df_inv_total["Medida"] == medida_v)
                        if not df_inv_total[filtro_inv].empty:
                            stock_actual = int(df_inv_total.loc[filtro_inv, "Cantidad"].values[0])
                            df_inv_total.loc[filtro_inv, "Cantidad"] = stock_actual + cant_v
                            guardar_inventario(df_inv_total)
                        
                        df_ventas_total = df_ventas_total.drop(venta_a_borrar)
                        guardar_venta(df_ventas_total)
                        st.warning("Venta eliminada del historial y stock devuelto al inventario.")
                        st.rerun()
        else:
            st.info("Aún no tienes ventas registradas.")
