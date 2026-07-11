from app.core.security import decrypt, encrypt


def test_encryption_roundtrip():
    plaintext = "بيانات حساسة للمتطوع"
    ciphertext = encrypt(plaintext)
    assert ciphertext != plaintext
    assert decrypt(ciphertext) == plaintext


def test_encryption_empty():
    assert decrypt(encrypt("")) == ""
