import os
import requests

# Coordenadas y zona configuradas
LATITUDE = -36.6219
LONGITUDE = -64.2882
ZONA_NOMBRE = "Santa Rosa, La Pampa"

# Credenciales seguras tomadas de las variables de entorno de GitHub
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def obtener_clima_actual():
  """Consulta la API de Open-Meteo para obtener el clima actual."""
  url = (
      f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude="
      f"{LONGITUDE}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_gusts_10m"
  )

  try:
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("current", {})
  except Exception as e:
    print(f"Error al consultar el servicio meteorológico: {e}")
    return None


def evaluar_alertas(clima):
  """Evalúa si las condiciones actuales superan umbrales de riesgo."""
  alertas = []

  viento = clima.get("wind_speed_10m", 0)
  rf_viento = clima.get("wind_gusts_10m", 0)
  precipitacion = clima.get("precipitation", 0)
  weather_code = clima.get("weather_code", 0)

  # Umbrales ajustables (viento > 35 km/h o ráfagas > 50 km/h)
  if viento > 35 or rf_viento > 50:
    alertas.append(
        f"⚠️ **Alerta de Viento Fuerte:** Viento a {viento} km/h (ráfagas de"
        f" {rf_viento} km/h)."
    )

  if precipitacion > 5:
    alertas.append(
        f"🌧️ **Alerta de Lluvia Intensa:** {precipitacion} mm registrados."
    )

  if weather_code in [95, 96, 99]:
    alertas.append(
        "⛈️ **Alerta de Tormenta Eléctrica:** Actividad de tormentas detectada en"
        " la zona."
    )

  return alertas


def enviar_alerta_telegram(mensaje):
  """Envía el mensaje de alerta por Telegram."""
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("Error: Faltan las credenciales de Telegram en las variables.")
    return

  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": f"🚨 **REPORTE DE ALERTA METEOROLÓGICA** ({ZONA_NOMBRE})\n\n"
      + mensaje,
      "parse_mode": "Markdown",
  }

  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Error al enviar mensaje por Telegram: {e}")


def verificar_meteorologia():
  print(f"Verificando clima para {ZONA_NOMBRE}...")
  clima = obtener_clima_actual()

  if not clima:
    return

  alertas = evaluar_alertas(clima)

  if alertas:
    mensaje_final = "\n".join(alertas)
    enviar_alerta_telegram(mensaje_final)
    print("¡Alerta enviada con éxito por Telegram!")
  else:
    print(
        "Condiciones meteorológicas normales. No se detectaron alertas"
        " vigentes."
    )


if __name__ == "__main__":
  verificar_meteorologia()
  
