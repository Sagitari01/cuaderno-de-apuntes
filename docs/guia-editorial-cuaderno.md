# Guía editorial del Cuaderno de apuntes

Estas convenciones orientan la creación y revisión de futuras lecciones del sitio público.

## Finalidad y redacción

- Material pedagógico autónomo: **explicar conceptos**, de menor a mayor dificultad, con ejemplos ficticios y lenguaje accesible.
- Mantener las explicaciones desarrolladas; las imágenes **acompañan**, no reemplazan, el texto.
- No incorporar instrucciones de actividades, entregables, rúbricas, evaluaciones formales ni referencias a sesiones privadas.
- Mantener el material público independiente de marcas, instituciones, clientes y datos personales de contextos privados.
- Evitar afirmaciones técnicas absolutas sin sustento; diferenciar recomendaciones, limitaciones y garantías.

## Ilustraciones

- Estética aprobada: **hoja de cuaderno rayada**, margen y espiral/perforaciones, trazos y letras de apariencia manual, colores suaves, iconos explicativos y anotaciones pedagógicas.
- Usar **el archivo original de la ilustración aprobada**, no reemplazarlo por una reimplementación SVG minimalista.
- **Una imagen, una idea:** priorizar diagramas, flechas, comparaciones y ejemplos mínimos. Evitar láminas con párrafos, tablas extensas o toda la lección condensada.
- Distribuir ilustraciones junto a los conceptos que explican, en vez de reunirlas todas al inicio o publicar un único póster recargado.
- Mantener los textos y matices pedagógicos en el apunte; las imágenes son apoyos simples y no deben reemplazar la explicación.
- Revisar que ninguna imagen contradiga las reglas escritas ni exponga información de actividades privadas.
- Incluir las láminas junto al concepto que aclaran; no generar imágenes para decorar.
- Publicar imágenes optimizadas en `contenido/<curso>/imagenes/` y verificar cada ruta en el repositorio.
- Cada imagen debe tener `alt` descriptivo, tamaño adaptable, y un botón discreto de expandir (arriba a la derecha) que abra la lámina completa en una pestaña nueva.
- Usar el mismo diseño y ubicación para el botón de todas las láminas de una lección.

## Navegación y autoevaluación

- Conservar el comportamiento de secciones desplegables previsto en la aplicación.
- En apuntes conceptuales, la autoevaluación puede ser **interactiva al final**, nunca convertida en una imagen. En apuntes de juego, puede reemplazarse por el acceso al recurso, un tutorial y un solucionario oculto tras confirmaciones.
- Para cada pregunta usar el formato que admite el visor:

```quiz
? ¿Qué caracteriza a un dato estructurado?
+ Tiene campos o columnas definidos.
- Necesariamente contiene una fotografía.
- No puede almacenarse en un sistema.
> Los campos definidos facilitan su validación y procesamiento.
```

- Cuando haya autoevaluación, verificar que cada pregunta tenga opciones, **una alternativa correcta** y explicación.
- Si se incluye un juego, comprobar el repositorio oficial y describir controles reales de la versión publicada. Las ilustraciones conceptuales no deben presentarse como capturas auténticas.
- Los solucionarios son opcionales y deben estar al final, ocultos detrás de varias confirmaciones; evitar mostrarlos sin una interacción explícita.
- Solo el material más reciente del índice se marca automáticamente como **Nuevo**.

## Lista de revisión antes de cerrar un cambio

1. Archivo actualizado y ruta registrada en `contenido/cursos.json`.
2. Ilustraciones **originales** publicadas y correctamente referenciadas.
3. Botones de ampliar visibles, accesibles y enlazados al archivo correspondiente.
4. Conceptos explicados con precisión; ejemplos ficticios y neutros.
5. Sin referencias a actividades, entregables o instituciones privadas.
6. Autoevaluación final compatible con el parser (`? + - >`), **o** juego con tutorial y solucionario escalonado, según el tipo de apunte.
7. Verificación de archivos y enlaces en GitHub; distinguir esa revisión de una prueba visual en el sitio desplegado.
