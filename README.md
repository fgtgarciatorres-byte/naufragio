# Naufragios

Herramienta auditable para investigar naufragios históricos de Canarias y sus rutas atlánticas hasta 1800.

La primera versión contiene agentes deterministas que pueden ejecutarse sin una API de IA:

- `investigador_de_fuentes`: descubre y registra nuevas fuentes del catálogo local.
- `buscador_de_evidencias`: recupera evidencias por términos y variantes.
- `extractor_de_entidades`: extrae barcos, lugares, fechas, cargas y personas.
- `resolutor_de_entidades`: relaciona variantes de nombres.
- `contraste`: detecta conflictos entre fuentes.
- `cartografia`: construye GeoJSON con incertidumbre.
- `orquestador`: conecta todos los agentes y genera un expediente verificable.

## Ejecutar

```text
python main.py --health
python main.py buscar "Armadas Canarias"
python main.py investigar-fuentes "naufragio Canarias"
python main.py expediente "Santa Ana"
```

La salida incluye citas con URL, título, tipo de fuente, fragmento, estado de verificación y fecha de acceso registrada. Los datos de `data/` son semillas públicas y una evidencia sintética claramente marcada para comprobar el flujo completo sin atribuir un naufragio ficticio a una fuente real.

## Fuentes iniciales

El catálogo incluye PARES/Archivo General de Indias, BNE Digital, Gallica, Library of Congress y RNOD. La aplicación no descarga documentos ni evita restricciones de acceso: registra el catálogo, consulta adaptadores autorizados y conserva únicamente metadatos y evidencias permitidas.

## Estado de verificación

La puntuación no equivale a una identificación arqueológica. Un resultado puede pasar las pruebas de software y seguir necesitando revisión historiográfica, consulta del documento original, contraste independiente y permisos patrimoniales.

