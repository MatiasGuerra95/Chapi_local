DETAIL_URL = "https://oficinajudicialvirtual.pjud.cl/ADIR_871/laboral/detalleCausaLaboral.php"

detail = sess.post(
    DETAIL_URL,
    data={"token": jwt, "competencia": "4"},
    headers={"X-Requested-With":"XMLHttpRequest",
             "Content-Type":"application/x-www-form-urlencoded"}
).text
# ahora parsea igual que antes:
litigantes  = HTMLParser(detail).css("#litigantesLab tbody tr")
relaciones  = HTMLParser(detail).css("#relacionesLab tbody tr")
