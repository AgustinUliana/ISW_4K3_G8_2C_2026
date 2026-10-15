from datetime import datetime, timedelta

from ecoharmony.reloj import RelojSistema


def test_el_reloj_del_sistema_devuelve_la_hora_actual():
    ahora = RelojSistema().ahora()

    assert abs(datetime.now() - ahora) < timedelta(seconds=5)
