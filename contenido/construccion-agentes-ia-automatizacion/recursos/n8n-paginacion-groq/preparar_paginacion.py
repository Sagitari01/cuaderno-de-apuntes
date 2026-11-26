from pathlib import Path
import shutil
p = Path('simulador_catalogo_seguro.py')
s = p.read_text(encoding='utf-8')
old = '            cuerpo = {"acceso": mecanismo, "libros": [datos_libro(t, completo) for t in CATALOGO]}'
new = '''            libros = [datos_libro(t, completo) for t in CATALOGO]
            cuerpo = {"acceso": mecanismo, "libros": libros}
            if "pagina" in consulta or "limite" in consulta:
                try:
                    pagina = int(consulta.get("pagina", ["1"])[0])
                    limite = int(consulta.get("limite", ["2"])[0])
                    if pagina < 1 or not 1 <= limite <= 100:
                        raise ValueError()
                except ValueError:
                    return self._responder(400, {"error": "paginacion_invalida"})
                inicio = (pagina - 1) * limite
                cuerpo.update({"libros": libros[inicio:inicio + limite],
                               "pagina": pagina, "limite": limite,
                               "total": len(libros),
                               "hay_mas": inicio + limite < len(libros)})'''
if new in s:
    print('La paginación ya está instalada.')
elif s.count(old) != 1:
    raise SystemExit('Versión diferente: no se modificó el archivo.')
else:
    updated = s.replace(old,new,1)
    compile(updated, str(p), 'exec')
    backup = p.with_suffix('.py.g17.bak')
    if backup.exists():
        raise SystemExit('Ya existe un respaldo. No se modificó el archivo.')
    shutil.copy2(p,backup)
    p.write_text(updated,encoding='utf-8')
    print('Paginación instalada; respaldo:',backup)
