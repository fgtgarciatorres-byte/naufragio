# Naufragios

Herramienta auditable para investigar naufragios hist�ricos de Canarias y sus rutas atl�nticas hasta 1800.

## Atlas visual

La interfaz est� en `index.html` y funciona como una carta de investigaci�n: carga `data/atlas.json`, filtra evidencias, muestra posiciones con incertidumbre, abre la ficha de cada registro y permite incorporar otro JSON desde el bot�n **Cargar JSON**. Para verla localmente:

```text
python -m http.server 8766
```

Despu�s abre `http://localhost:8766/`. La vista es est�tica y no presenta una posici�n de pecio como exacta ni convierte la evidencia sint�tica en un hecho hist�rico.

La primera versi�n contiene agentes deterministas que pueden ejecutarse sin una API de IA:

- `investigador_de_fuentes`: descubre y registra nuevas fuentes del cat�logo local.
- `buscador_de_evidencias`: recupera evidencias por t�rminos y variantes.
- `extractor_de_entidades`: extrae barcos, lugares, fechas, cargas y personas.
- `resolutor_de_entidades`: relaciona variantes de nombres.
- `contraste`: detecta conflictos entre fuentes.
- `cartografia`: construye GeoJSON con incertidumbre.
- `investigador_de_pleitos`: identifica pleitos, reclamaciones, p�rdidas econ�micas, arribadas y mercanc�as como pistas jur�dicas separadas.
- `investigador_persona_amaro_pargo`: agente independiente para Amaro Pargo, sus alias, red de barcos y personas, rutas Canarias-Caribe y fuentes espa�olas, francesas e inglesas.
- `orquestador`: conecta todos los agentes y genera un expediente verificable.

La etiqueta `legal_lead` significa que existe una pista jur�dica documentada. Una demanda, una reclamaci�n o un pleito de acreedores no confirma por s� solo un naufragio; el expediente original debe leerse y contrastarse.

Para ejecutar el agente biogr�fico: `python main.py amaro "Amaro Pargo"`. Devuelve alias, l�neas de b�squeda por idioma, propiedades, herencias, inventarios, rutas caribe�as, resultados vinculados y huecos pendientes. La subl�nea de La Laguna conserva referencias a protocolos notariales del AHPSCT, el fondo Ossuna y Santa Catalina de Siena.

Se han incorporado tres entradas verificables de PARES: `ESCRIBANIA,1029A` (1661, pleito de acreedores sobre San Juan Coronado y Nuestra Se�ora de Regla), `ESCRIBANIA,1047A` (1695, reclamaci�n por el San Jos� y sus frutos) y la ficha `87489` (1584, arribada de La Concepci�n cargada de mercanc�as y referencia a un juez de registro de Tenerife).

La cobertura canaria incluye ahora El Museo Canario, su biblioteca y la red BICA, los Archivos Hist�ricos Provinciales de Las Palmas y Santa Cruz de Tenerife, Memoria Digital de Canarias, Jable, LAVA y una gu�a digital de fondos del AGI conservada en la ULPGC. Esta �ltima se�ala expedientes de 1756-1764 sobre permisos de navegaci�n, registros de nav�os, cargas, entradas y salidas en Canaria y Tenerife.

## Ejecutar

```text
python main.py --health
python main.py buscar "Armadas Canarias"
python main.py investigar-fuentes "naufragio Canarias"
python main.py expediente "Santa Ana"
```

La salida incluye citas con URL, t�tulo, tipo de fuente, fragmento, estado de verificaci�n y fecha de acceso registrada. Los datos de `data/` son semillas p�blicas y una evidencia sint�tica claramente marcada para comprobar el flujo completo sin atribuir un naufragio ficticio a una fuente real.

## Fuentes iniciales

El cat�logo incluye PARES/Archivo General de Indias, BNE Digital, Gallica, Library of Congress y RNOD. La aplicaci�n no descarga documentos ni evita restricciones de acceso: registra el cat�logo, consulta adaptadores autorizados y conserva �nicamente metadatos y evidencias permitidas.

## Estado de verificaci�n

La puntuaci�n no equivale a una identificaci�n arqueol�gica. Un resultado puede pasar las pruebas de software y seguir necesitando revisi�n historiogr�fica, consulta del documento original, contraste independiente y permisos patrimoniales.

