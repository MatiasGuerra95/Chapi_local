from selectolax.parser import HTMLParser

html = r.text                          # la respuesta completa
tree = HTMLParser(html)

fila = tree.css_first("tr")            # primera fila real
tds  = [td.text(strip=True) for td in fila.css("td")]
rit, tribunal, carat, fecha, estado = tds[1:6]

token = fila.css_first("a.toggle-modal").attributes["onClick"]
# token = detalleCausaLaboral('<AQUÍ_VA_EL_JWT>')
jwt = token.split("('",1)[1].split("')",1)[0]
