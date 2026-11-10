from datetime import datetime
import os
import pandas as pd
import streamlit as st

ARCHIVO_DB = "inventario_general.xlsx"
PORCENTAJE_IVA = 0.16  # 16% de IVA
PASSWORD_SECRETO = "1234"  # Puedes cambiar la contraseña aquí cuando gustes


def inicializar_archivo():
  if not os.path.exists(ARCHIVO_DB):
    with pd.ExcelWriter(ARCHIVO_DB, engine="openpyxl") as writer:
      pd.DataFrame(
          columns=[
              "Fecha",
              "Tipo",
              "Proveedor/Cliente",
              "Medida",
              "Cantidad",
              "Precio Base",
              "Precio Neto (c/IVA)",
              "Total Neto",
          ]
      ).to_excel(writer, sheet_name="Movimientos", index=False)


# Configuración visual de la app
st.set_page_config(
    page_title="Control de Llantas", page_icon="🛞", layout="centered"
)
inicializar_archivo()

# --- PANTALLA DE INICIO DE SESIÓN (SEGURIDAD) ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  st.title("🔐 Acceso Seguro - Inventario")
  st.write("Introduce tu contraseña para acceder al sistema:")
  password = st.text_input("Contraseña", type="password")

  if st.button("Iniciar Sesión"):
    if password == PASSWORD_SECRETO:
      st.session_state.autenticado = True
      st.rerun()
    else:
      st.error("Contraseña incorrecta.")
  st.stop()  # Detiene la ejecución si no ha puesto la contraseña correcta

# --- APLICACIÓN PRINCIPAL (UNA VEZ ADENTRO) ---
st.title("🛞 Gestor de Llantas y Ventas")

# Menú lateral táctil (ideal para celular o PC)
st.sidebar.title("Menú Principal")
menu = st.sidebar.radio(
    "Selecciona una opción:",
    ["Registrar Compra", "Registrar Venta", "Inventario Actual", "Historial"],
)

df = pd.read_excel(ARCHIVO_DB, sheet_name="Movimientos")

if menu in ["Registrar Compra", "Registrar Venta"]:
  tipo = "COMPRA" if menu == "Registrar Compra" else "VENTA"
  st.subheader(f"Registrar {tipo}")

  with st.form(key=f"form_{tipo}"):
    tercero = (
        st.text_input(
            "Nombre del Proveedor (Compra) o Cliente (Venta):"
        ).strip().upper()
    )
    medida = st.text_input("Medida de la llanta (ej. 195/65R15)").strip().upper()
    cantidad = st.number_input("Cantidad de piezas:", min_value=1, step=1)
    precio_base = st.number_input(
        "Precio unitario SIN IVA ($):", min_value=0.0, step=10.0
    )

    submit = st.form_submit_button(f"Guardar {tipo}")

    if submit:
      if not tercero or not medida:
        st.warning("Por favor completa el nombre y la medida.")
      else:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        precio_neto = precio_base * (1 + PORCENTAJE_IVA)
        total_neto = cantidad * precio_neto
        cant_guardar = -cantidad if tipo == "VENTA" else cantidad

        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha,
            "Tipo": tipo,
            "Proveedor/Cliente": tercero,
            "Medida": medida,
            "Cantidad": cant_guardar,
            "Precio Base": precio_base,
            "Precio Neto (c/IVA)": precio_neto,
            "Total Neto": total_neto,
        }])

        df = pd.concat([df, nuevo_registro], ignore_index=True)
        with pd.ExcelWriter(ARCHIVO_DB, engine="openpyxl") as writer:
          df.to_excel(writer, sheet_name="Movimientos", index=False)

        st.success(
            f"¡{tipo} registrada con éxito! Precio Neto con IVA:"
            f" ${precio_neto:,.2f}"
        )

elif menu == "Inventario Actual":
  st.subheader("📦 Stock Disponible por Medida")
  if df.empty:
    st.info("Aún no hay registros.")
  else:
    stock = (
        df.groupby("Medida")["Cantidad"]
        .sum()
        .reset_index(name="Stock Disponible")
    )
    st.dataframe(stock, use_container_width=True)

elif menu == "Historial":
  st.subheader("📋 Historial Completo")
  if df.empty:
    st.info("No hay movimientos registrados.")
  else:
    st.dataframe(df, use_container_width=True)