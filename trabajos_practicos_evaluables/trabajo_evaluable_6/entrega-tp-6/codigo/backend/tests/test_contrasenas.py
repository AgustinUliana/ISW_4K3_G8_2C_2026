from ecoharmony.contrasenas import hashear, verificar


def test_el_hash_no_contiene_la_contrasena_en_texto_plano():
    assert "secreto1" not in hashear("secreto1")


def test_dos_hashes_de_la_misma_contrasena_son_distintos_por_la_sal():
    assert hashear("secreto1") != hashear("secreto1")


def test_verificar_acepta_la_contrasena_correcta_y_rechaza_otra():
    almacenado = hashear("secreto1")

    assert verificar("secreto1", almacenado)
    assert not verificar("secreto2", almacenado)


def test_verificar_rechaza_un_hash_con_formato_invalido():
    assert not verificar("secreto1", "esto-no-es-un-hash")
