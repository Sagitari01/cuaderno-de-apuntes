# Cuaderno de apuntes

Sitio web estático para publicar material de apoyo de clases: lecturas, ejercicios, código, enlaces y autoevaluaciones. Se escribe todo en archivos `.md`; el sitio los ordena por curso y semana, y cada alumno puede buscar, marcar lo que ya vio y llevar su avance.

No necesita servidor ni base de datos. Funciona en GitHub Pages, y el progreso y el tema (claro/oscuro) se guardan en el navegador de cada persona.

## Para qué sirve

- Subir material nuevo clase a clase con solo agregar un `.md` y una línea de registro.
- Que los alumnos tengan un lugar único, ordenado y con buscador.
- Practicar con ejercicios y quizzes que responden al instante.

Ahora está vacío: la estructura está lista y los cursos se van agregando.

## Publicar

1. Settings → Pages → Deploy from branch → `main` / root.
2. Abre `https://sagitari01.github.io/cuaderno-de-apuntes/`.

## Agregar un curso

En `contenido/cursos.json`, dentro de `cursos`:

```json
{
  "id": "mi-curso",
  "codigo": "ABC123",
  "titulo": "Nombre del curso",
  "descripcion": "Una o dos frases sobre el curso.",
  "semanas": [
    { "titulo": "Semana 1", "tema": "Tema de la semana", "materiales": [] }
  ]
}
```

## Agregar material

1. Crea un `.md` en `contenido/<curso>/`, por ejemplo `contenido/mi-curso/01-intro.md`.
2. Regístralo en la semana que corresponda de `contenido/cursos.json`:
   ```json
   { "id": "intro", "titulo": "Título visible", "tipo": "lectura", "archivo": "mi-curso/01-intro.md", "nuevo": true }
   ```
   `tipo`: `lectura`, `codigo`, `ejercicio`, `enlaces` o `quiz`. `nuevo: true` muestra la etiqueta "Nuevo".
3. Haz commit y push. Aparece al publicarse.

## Bloques especiales en Markdown

Ejercicio (recuadro destacado):

````
```ejercicio
Texto del ejercicio, admite **markdown**.
```
````

Nota:

````
```nota
Un consejo o aclaración.
```
````

Quiz con respuesta inmediata (`?` pregunta, `+` correcta, `-` incorrecta, `>` explicación):

````
```quiz
? ¿Pregunta?
- Opción incorrecta
+ Opción correcta
> Explicación que aparece al responder.
```
````

Todo bloque de código normal (```python, ```bash…) trae botón "Copiar". Los enlaces externos se abren en otra pestaña.

## Probar en tu computador

Los archivos se cargan con `fetch`, así que necesitas un servidor local:

```bash
python -m http.server
```

y abre `http://localhost:8000`.

## Estructura

| Archivo | Qué es |
|---|---|
| `Guias.dc.html` | El sitio completo (componente único) |
| `assets/industry.css` | Estilos y colores |
| `support.js` | Runtime del componente; es generado, no se edita |
| `contenido/cursos.json` | Índice de cursos, semanas y materiales |
| `contenido/<curso>/*.md` | El material |
