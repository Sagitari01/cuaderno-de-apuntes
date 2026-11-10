# Modelamiento de procesos: AS-IS y TO-BE

## Propósito

Antes de automatizar un proceso, conviene comprender cómo funciona actualmente y qué cambios se esperan conseguir.

## AS-IS: situación actual

El modelo **AS-IS** describe el proceso tal como ocurre hoy, incluyendo las actividades, participantes, decisiones, herramientas y posibles dificultades.

Para documentarlo, registra:

- El evento que inicia el proceso.
- Las acciones que se ejecutan y quién las realiza.
- Las decisiones que cambian el flujo.
- La información que entra y sale.
- Los pasos repetitivos, esperas y errores frecuentes.

## TO-BE: situación propuesta

El modelo **TO-BE** describe cómo se espera que funcione el proceso después de introducir mejoras. Puede incorporar automatizaciones, validaciones o cambios en las responsabilidades.

Una propuesta útil debe indicar qué pasos cambian, cuáles se mantienen y cómo se comprobará que el resultado mejora el proceso original.

## Ejemplo de trabajo

**Situación:** un equipo recibe solicitudes por correo electrónico, copia cada solicitud a una planilla y envía una confirmación manual.

**AS-IS:** recibir correo → leer solicitud → registrar datos → revisar campos → redactar confirmación → enviar respuesta.

**TO-BE:** recibir solicitud → extraer datos → validar campos → registrar información → generar confirmación → derivar excepciones a revisión humana.

```nota
Automatizar no significa eliminar todas las decisiones humanas. Los casos ambiguos o excepcionales pueden requerir revisión.
```

## Preguntas para el análisis

1. ¿Qué actividad consume más tiempo en el proceso actual?
2. ¿Dónde podrían producirse errores de transcripción?
3. ¿Qué pasos podrían automatizarse mediante reglas claras?
4. ¿Qué situaciones deberían mantenerse bajo supervisión humana?

```ejercicio
Elige un proceso cotidiano de al menos cinco pasos. Describe su versión **AS-IS** y luego una propuesta **TO-BE**. Señala dos mejoras concretas y una situación que requiera intervención humana.
```
