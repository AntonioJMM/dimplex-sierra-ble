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
- Formularios propios de credenciales y reautenticación, independientes de la integración oficial Tuya.
- Confirmación explícita del descubrimiento Bluetooth y reintentos automáticos ante fallos temporales.

## Hardware confirmado

| Producto | Modelo | Tuya product ID | Estado |
|---|---|---|---|
| Dimplex Sierra 48 | `SIL48` / `X-SIL48` | `0fsaqmtu` | Validado físicamente |

El nombre Bluetooth `TY` no demuestra compatibilidad: muchos productos Tuya BLE lo utilizan.

## Requisitos

- Home Assistant con la integración Bluetooth funcionando.
- Adaptador o proxy Bluetooth conectable y con cobertura de la chimenea.
- **UUID BLE de Tuya**, **ID de dispositivo**, **clave local de 16 caracteres** y **product ID** (`0fsaqmtu`) de tu chimenea.
- Home Assistant `2026.10.0` o posterior para la rama actualmente probada.

### Obtención de credenciales

Obtén los datos desde tu propia cuenta Tuya autorizada, por ejemplo mediante la [plataforma de desarrollo Tuya](https://platform.tuya.com/). Su disponibilidad depende de la cuenta, región y permisos de API. El UUID BLE no es la dirección Bluetooth/MAC. Esta integración no crea un proyecto cloud, extrae credenciales de otras integraciones ni inicia sesión en Tuya por ti. Sin los cuatro datos no puede completarse la configuración; no los adivines ni restablezcas la chimenea para probar.

La integración oficial Tuya de Home Assistant **no es necesaria**. Introduces los datos en el formulario propio y se guardan en la entrada de configuración de esta integración. El control posterior usa BLE local.

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

1. Configura Bluetooth y obtén las credenciales indicadas anteriormente.
2. Mantén la chimenea alimentada, anunciándose y dentro de cobertura; conserva la calefacción apagada durante las comprobaciones iniciales.
3. Añade **Dimplex Sierra BLE** y selecciona tu chimenea. Si aparece por descubrimiento automático, confirma primero que el anuncio genérico de Tuya corresponde a tu Sierra 48.
4. Introduce UUID BLE, ID de dispositivo, clave local y product ID. El formulario comprueba el formato, no la autenticación Bluetooth. La configuración inicial intenta después autenticarse y leer, sin escribir órdenes de control.
5. Home Assistant reintentará automáticamente los fallos temporales de anuncio o conexión. Para corregir credenciales, elige **Reconfigurar** en el menú de esta integración e introduce de nuevo los cuatro datos; se conservarán la entrada y sus entidades.

### Actualización desde 0.3.x

Haz un backup de Home Assistant antes de actualizar. Se migra la entrada existente sin cambiar su ID ni los identificadores únicos de las entidades. Como las entradas antiguas no guardaban credenciales, Home Assistant solicitará reautenticación: introduce los datos de la misma chimenea en el formulario propio. No elimines la entrada ni vuelvas a vincular la chimenea. Sus entidades pueden estar no disponibles hasta aportar los datos.

El protocolo BLE y los controles se validaron físicamente en 0.3.0. Los nuevos flujos de credenciales y migración de 0.4.0 tienen pruebas automatizadas, pero todavía no se han revalidado físicamente. Para revertir con seguridad, restaura el backup anterior: las versiones antiguas no pueden leer la entrada de configuración de versión 2.

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

La clave local, UUID BLE, ID de dispositivo y dirección Bluetooth se guardan en la entrada de configuración de Home Assistant de esta integración. Protege el directorio de configuración y los backups: los campos de contraseña ocultan el texto, pero no cifran el almacenamiento. La integración no pretende escribir credenciales en los logs; el logger del transporte incluido permanece silenciado porque el DEBUG del upstream puede contener identificadores.

Antes de abrir una incidencia, elimina cualquier dato identificativo y revisa manualmente capturas y diagnósticos. Consulta [SECURITY.md](SECURITY.md).

## Limitaciones conocidas

- Solo se admite el product ID `0fsaqmtu`.
- Solo se ha validado una unidad física.
- Debes obtener tus credenciales BLE mediante una cuenta Tuya autorizada; no hay extracción automática.
- DP103 sigue sin identificar.
- Fahrenheit no se ha validado físicamente al mismo nivel que Celsius.

## Licencia y atribución

El proyecto usa licencia MIT. El transporte Tuya BLE incluido procede de `ShonP40/Tuya-BLE`, commit `e9d09366ccddaf793f052817f6c7dcaab3d821a2`, y deriva de `PlusPlus-ua/ha_tuya_ble`.

Consulta [LICENSE](LICENSE) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
