import re

def validar_rfc (rfc):
    #Valida RFC mexicano con homoclave#
    patron = r'^[A-Z]{4}\d{6}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[A-Z\d]{3}$' # TU CODIGO AQUI
    return bool(re. fullmatch (patron , rfc))

def validar_matricula_uam ( matricula ):
    #Valida matricula UAM#
    patron = r'^\d{10}$' # TU CODIGO AQUI
    return bool(re. fullmatch (patron , matricula ))

def validar_ipv4 (ip):
    """Valida direccion IPv4"""
    patron = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$' # TU CODIGO AQUI
    return bool(re. fullmatch (patron , ip))

def validar_password_fuerte (password):
    """Valida contraseña fuerte"""
    # TU CODIGO AQUI
    # Pista: Usa lookahead assertions (?=...)
    patron = r'^(?=(?:.*[A-Z]){2})(?=(?:.*[a-z]){2})(?=(?:.*\d){2})(?=.*[!@#$%^&*]).{10,}$'    
    return bool(re.match(patron, password))
    pass

# Casos de prueba
if __name__ == "__main__":
    # RFC
    validar_rfc ("AAAA850101ABC") #== True
    validar_rfc ("AAA850101ABC") #== False

    # Matricula
    validar_matricula_uam ("2223456789") #== True
    validar_matricula_uam ("223456789") #== False

    # IPv4
    validar_ipv4 ("192.168.1.1") #== True
    validar_ipv4 ("256.1.1.1") #== False

    # Password
    validar_password_fuerte ("Abc123!Xyz456#") #== True
    validar_password_fuerte ("Password1!") #== False

    print("Todos los tests pasaron!")