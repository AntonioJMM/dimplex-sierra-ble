# Dimplex Sierra BLE para Home Assistant

Control Bluetooth local para determinadas chimeneas eléctricas Dimplex Sierra que usan Tuya BLE V4.2 sobre el servicio `0xFD50`.

> [!IMPORTANT]
> Este es un proyecto comunitario independiente. No está afiliado, respaldado ni soportado por Dimplex, Tuya o Home Assistant.
>
> La integración está actualmente en fase **beta**. Se ha validado físicamente en una Sierra 48 con product ID `0fsaqmtu`. No debe suponerse que otros productos usan los mismos datapoints.

[English documentation](README.md)

## Funciones

- Sondeo y control BLE local.
- Encendido general y calefacción.
- Temperatura objetivo y calor continuo.
- Efecto y brillo de llama.
- Efecto y brillo del lecho de brasas.
- Encendido y apagado del sonido.
- Temporizador de 0 a 8 horas.
- Diagnóstico del bloqueo físico del calefactor.
- Verificación por lectura posterior de cada escritura.
- Desconexión BLE después de cada operación.
- Reutilización en memoria de las credenciales Tuya, sin copiarlas a la entrada de configuración.

## Hardware confirmado

| Producto | Modelo | Tuya product ID | Estado |
|---|---|---|---|
| Dimplex Sierra 48 | `SIL48` / `X-SIL48` | `0fsaqmtu` | Validado físicamente |

El nombre Bluetooth `TY` no demuestra compatibilidad: muchos productos Tuya BLE lo utilizan.

## Requisitos

- Home Assistant con la integración Bluetooth funcionando.
- Adaptador o proxy Bluetooth conectable y con cobertura de la chimenea.
- Integración oficial **Tuya** configurada y con la chimenea presente.
- Home Assistant `2026.10.0` o posterior para la rama actualmente probada.

### Dependencia importante de Tuya

Las órdenes son locales, pero la integración obtiene en memoria el UUID BLE y la clave local desde los datos de ejecución de la integración oficial Tuya. Es una interfaz interna que podría cambiar en futuras versiones de Home Assistant. La clave no se escribe en los archivos ni en la entrada de configuración de esta integración.

## Instalación

### Repositorio personalizado de HACS

1. Abre HACS y entra en **Integraciones**.
2. Abre el menú y selecciona **Repositorios personalizados**.
3. Añade `https://github.com/AntonioJMM/dimplex-sierra-ble` con categoría **Integración**.
4. Instala **Dimplex Sierra BLE**.
5. Reinicia Home Assistant.

El proyecto todavía no forma parte de la lista predeterminada de HACS.

### Instalación manual

1. Descarga una release etiquetada.
2. Copia `custom_components/dimplex_sierra_ble` en `/config/custom_components/`.
3. Reinicia Home Assistant.
4. Abre **Ajustes → Dispositivos y servicios → Añadir integración**.
5. Busca **Dimplex Sierra BLE**.

## Configuración

1. Configura Bluetooth en Home Assistant.
2. Configura la integración oficial Tuya y confirma que contiene la chimenea.
3. Enciende la chimenea para que anuncie por BLE.
4. Añade **Dimplex Sierra BLE** y selecciona el dispositivo descubierto.

No publiques en una incidencia contraseñas, claves locales, UUID, direcciones Bluetooth, identificadores Tuya ni números de serie.

## Entidades

La integración crea 13 entidades:

- Entidad climática.
- Interruptores de encendido, calefacción y sonido.
- Selectores de termostato, llama y brasas.
- Controles de brillo de llama, brillo de brasas y temporizador.
- Sensor binario del bloqueo físico del calefactor.
- Sensores diagnósticos de unidad y DP103.

DP103 se muestra únicamente como dato diagnóstico. Ha producido valores incompatibles con una temperatura ambiente real y no se usa como `current_temperature`.

## Seguridad de uso

- La integración no anula remotamente el bloqueo físico del calefactor.
- Encendido general y calefacción son datapoints independientes.
- Mantén la calefacción apagada durante las primeras pruebas.
- No crees automatizaciones de calefacción desatendidas hasta validar tu hardware.
- DP108 tarda unos segundos en reflejar el cambio de sonido, por lo que tiene una lectura de verificación adicional.
- Si una orden no puede verificarse, Home Assistant devuelve un error en lugar de asumir éxito.

## Privacidad y logs

La integración no pretende registrar ni guardar la clave local Tuya, UUID Tuya, dirección Bluetooth o ID del dispositivo. El logger del transporte incluido permanece silenciado porque el DEBUG del upstream puede contener identificadores.

Antes de abrir una incidencia, elimina cualquier dato identificativo y revisa manualmente capturas y diagnósticos. Consulta [SECURITY.md](SECURITY.md).

## Limitaciones conocidas

- Solo se admite el product ID `0fsaqmtu`.
- Solo se ha validado una unidad física.
- La obtención de credenciales depende de detalles internos de Tuya.
- DP103 sigue sin identificar.
- Fahrenheit no se ha validado físicamente al mismo nivel que Celsius.

## Licencia y atribución

El proyecto usa licencia MIT. El transporte Tuya BLE incluido procede de `ShonP40/Tuya-BLE`, commit `e9d09366ccddaf793f052817f6c7dcaab3d821a2`, y deriva de `PlusPlus-ua/ha_tuya_ble`.

Consulta [LICENSE](LICENSE) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
