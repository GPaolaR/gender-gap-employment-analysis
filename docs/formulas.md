# Fórmulas del proyecto: brecha de género en el empleo
 
Resumen de las fórmulas, fichas de gráficos y modelo de tablas por pregunta guía (Argentina, Brasil, Chile, Colombia, Uruguay; datos del Banco Mundial / OIT, 1995–2025).
 
## Convenciones
 
- **H** = hombres, **M** = mujeres.
- **u** (desempleo) y **v** (empleo vulnerable) van como fracción en las fórmulas: 10% = 0.10.
- Las brechas se calculan **año por año** y después se promedian por periodo.
- Periodos de comparación: 1995–1997 vs 2022–2024 (2025 queda fuera del promedio por ser probablemente proyección de la OIT).
- Unidades: las diferencias entre tasas se expresan en **pp**; el % se usa solo para "qué parte de la brecha".
- EPR y Q se calculan desde LFP, u y v (no se usa la EPR publicada) para que las descomposiciones cierren exactas.
- **Signo de las brechas: positivo = desventaja de las mujeres.** Por eso EPR y Q se restan H − M, y vulnerable M − H. El índice de Duncan no tiene signo.
## Indicadores (códigos WDI)
 
| Símbolo | Indicador | Código |
|---|---|---|
| LFP | Tasa de participación (15+) | SL.TLF.CACT.FE/MA.ZS |
| u | Desempleo (% de la fuerza laboral) | SL.UEM.TOTL.FE/MA.ZS |
| EPR | Empleo / población (15+) | SL.EMP.TOTL.SP.FE/MA.ZS |
| v | Empleo vulnerable (% del empleo) | SL.EMP.VULN.FE/MA.ZS |
| agr, ind, serv | Empleo por sector (% del empleo) | SL.AGR/IND/SRV.EMPL.FE/MA.ZS |
 
---
 
## A1. Brecha de empleo
 
```
EPR        = LFP × (1 − u)
Brecha_EPR = EPR_H − EPR_M
Cambio     = Brecha(1995–97) − Brecha(2022–24)    → positivo = se redujo
```
 
> En [país], la tasa de empleo de las mujeres fue en promedio [X] pp menor que la de los hombres en 1995–1997 y [Y] pp menor en 2022–2024: la brecha [se redujo / se amplió] [|X − Y|] pp entre ambos periodos.
 
## A2. ¿Participación o desempleo?
 
```
Parte_participación = (LFP_H − LFP_M) × (1 − u_H)
Parte_desempleo     = LFP_M × (u_M − u_H)
Control             : Parte_participación + Parte_desempleo = Brecha_EPR
% de cada parte     = Parte ÷ (suma de las dos) × 100
```
 
> En [país], de los [X] pp de brecha de empleo en 1995–1997, el [P1]% se explicaba porque las mujeres no participaban y el [D1]% porque, participando, no conseguían empleo. En 2022–2024 fue [P2]% y [D2]%.
 
## C1. Brecha de empleo vulnerable (entre ocupados)
 
```
Brecha_v = v_M − v_H                      → positivo = las mujeres están peor
Cambio   = |Brecha(1995–97)| − |Brecha(2022–24)|
Si el signo cambia entre periodos → "se invirtió"
```
 
Nota: el indicador es % de los ocupados, no de la población. Ojo con el efecto selección (si entran más mujeres al mercado, puede subir su empleo vulnerable sin que nada haya empeorado).
 
> En [país], el porcentaje de mujeres ocupadas con empleo vulnerable fue en promedio [X] pp [mayor / menor] que el de los hombres en 1995–1997 y [Y] pp [mayor / menor] en 2022–2024: la brecha [se redujo / se amplió / se invirtió] [|X − Y|] pp.
 
## C2. Segregación por sectores (índice de Duncan)
 
```
D = ½ × ( |agr_M − agr_H| + |ind_M − ind_H| + |serv_M − serv_H| )
Sector con mayor diferencia = el de mayor |s_M − s_H|
Control: agr + ind + serv ≈ 100 para cada sexo
```
 
D (en %) = porcentaje de mujeres ocupadas que tendría que cambiar de sector para igualar la distribución de los hombres. Mide diferencia, no desventaja: es contexto para C1, no entra en S1. Con solo 3 sectores amplios subestima la segregación real.
 
> En [país], el [D1]% de las mujeres ocupadas tendría que cambiar de sector para igualar la distribución de los hombres en 1995–1997, y el [D2]% en 2022–2024. La mayor diferencia está en [sector]: [F]% de las mujeres frente a [M]% de los hombres.
 
## K1. Crisis (2008 y pandemia)
 
```
A, B, C        = Brecha_EPR promedio antes / durante / después
Δ_crisis       = B − A          → positivo = se amplió
Δ_recuperación = C − A          → |C − A| < 0.5 pp = "volvió al nivel previo"
¿Quién la movió?   ΔEPR_H = EPR_H(durante) − EPR_H(antes)
                   ΔEPR_M = EPR_M(durante) − EPR_M(antes)
```
 
| Crisis | Antes | Durante | Después |
|---|---|---|---|
| 2008 | 2005–2007 | 2008–2009 | 2010–2012 |
| Pandemia | 2017–2019 | 2020–2021 | 2022–2024 |
 
> En [país], la brecha de empleo era de [A] pp antes de la crisis, [B] pp durante y [C] pp después: durante la crisis [se amplió / se redujo / no cambió] y después [volvió / no volvió] a su nivel previo. El cambio se debió sobre todo a [las mujeres / los hombres / ambos].
 
## S1. ¿Acceso o calidad? (la tesis)
 
```
Q                    = EPR × (1 − v)  =  LFP × (1 − u) × (1 − v)
Brecha_Q             = Q_H − Q_M
Contribución_acceso  = (EPR_H − EPR_M) × (1 − v_H)
Contribución_calidad = EPR_M × (v_M − v_H)
Control              : acceso + calidad = Brecha_Q
% acceso             = acceso ÷ Brecha_Q × 100
```
 
Q = de cada 100 personas de 15+, cuántas tienen empleo no vulnerable. La brecha Q contiene acceso y calidad. La forma "Q_H − Q_M" da solo el total; la forma descompuesta da las partes (mismo valor).
 
Versión de tres partes (opcional):
 
```
Participación = (LFP_H − LFP_M) × (1 − u_H) × (1 − v_H)
Desempleo     = LFP_M × (u_M − u_H) × (1 − v_H)
Calidad       = LFP_M × (1 − u_M) × (v_M − v_H)
```
 
> En [país], de cada 100 personas en edad de trabajar, las mujeres tenían en promedio [Q1] pp menos empleo no vulnerable que los hombres en 1995–1997 y [Q2] pp menos en 2022–2024 (la brecha [se redujo / se amplió] [|Q1 − Q2|] pp). En ambos periodos la brecha se explica sobre todo por [el acceso / la calidad]: el acceso pesó [A1]% en 1995–1997 y [A2]% en 2022–2024, por lo que el peso de la calidad [aumentó / disminuyó].
 
Si la contribución de calidad es negativa, cambiar la redacción: "la calidad reduce la brecha en ___ pp".
 
### Cómo se obtiene la descomposición (la escalera)
 
Se parte de los valores de los hombres y se cambia **un factor a la vez** por el de las mujeres. Cada caída se atribuye al único factor que cambió. Ejemplo (H: LFP 70, u 7%, v 25%; M: LFP 50, u 10%, v 30%):
 
| Escalón | Q | Caída |
|---|---|---|
| Hombres (70 × 0.93 × 0.75) | 48.8 | |
| Cambia participación (50 × 0.93 × 0.75) | 34.9 | 13.9 participación |
| Cambia desempleo (50 × 0.90 × 0.75) | 33.8 | 1.1 desempleo |
| Mujeres (50 × 0.90 × 0.70) | 31.5 | 2.3 calidad |
 
Total 17.3 = 48.8 − 31.5. Acceso 87%, calidad 13%.
 
### Notas
 
- La brecha de un producto **no** es el producto de las brechas: hay que usar la escalera.
- Los hombres son la referencia; los factores ya cambiados en la escalera toman valores de mujeres, los pendientes de hombres. Por eso las fórmulas mezclan H y M.
- El orden de la escalera (participación → desempleo → calidad) sigue la lógica del embudo; con otro orden los pesos cambian un poco. Prueba de robustez: calcular también el orden inverso.
- La contribución de calidad puede ser negativa (las mujeres ocupadas tienen menos empleo vulnerable): resultado válido.
- "No vulnerable" ≠ "empleo decente" (incluye asalariados informales).
- Llamar "contribución" (no "brecha") a las partes, para no confundirlas con la brecha EPR o la brecha de vulnerabilidad.
---
 
## Fichas de gráficos
 
Navegación: selector de país en cada página (un país a la vez). Los títulos llevan huecos hasta ver los datos.
 
| Pregunta | Tipo | Eje X | Eje Y | Series | Extras | Título |
|---|---|---|---|---|---|---|
| **S1** | Barras apiladas por año (valores negativos bajo 0) | Año 1995–2025 | Contribución (pp) | Acceso, Calidad (opcional: participación, desempleo, calidad) | Etiqueta con % acceso; 2025 marcado provisional | "El __% de la brecha de empleo no vulnerable se explica por el acceso, no por la calidad" |
| **A1** | Líneas | Año 1995–2025 | EPR (%) | Hombres, Mujeres | Crisis sombreadas (2008–09, 2020–21); 2025 punteado | "La brecha de empleo se [redujo / amplió] de __ a __ pp entre 1995–97 y 2022–24" |
| **A2** | Barras 100% apiladas por año | Año 1995–2025 | % de la brecha EPR | Participación, Desempleo | | "La brecha de empleo se explica en un __% por la menor participación de las mujeres" |
| **C1** | Líneas | Año 1995–2025 | Empleo vulnerable (% de ocupados) | Hombres, Mujeres | Crisis sombreadas; 2025 punteado | "La brecha de empleo vulnerable se [redujo / amplió / invirtió] de __ a __ pp" |
| **C2a** | 4 barras 100% apiladas | M 1995–97, H 1995–97, M 2022–24, H 2022–24 | % del empleo de cada sexo | Agricultura, Industria, Servicios | | "La segregación [aumentó / disminuyó]: el empleo de las mujeres se concentró aún más en [sector]" |
| **C2b** | Línea | Año 1995–2025 | Índice D (%) | Índice de Duncan | | (acompaña a C2a) |
| **K1a / K1b** | Líneas (zoom 8 años) | 2005–2012 / 2017–2024 | EPR (%) | Hombres, Mujeres | Crisis sombreada; línea punteada con la brecha promedio de antes | "En [año] la brecha [se redujo] porque [los hombres] perdieron más empleo, y para [año] [volvió / no volvió] a su nivel previo" |
 
### Páginas del dashboard
 
| Página | Contenido | Gráficos |
|---|---|---|
| 1. La respuesta | La tesis en una frase | S1 |
| 2. Acceso | ¿Cuántas menos mujeres trabajan y por qué? | A1, A2 |
| 3. Calidad | ¿Peor empleo y dónde trabajan? | C1, C2a, C2b |
| 4. Crisis | 2008 y pandemia | K1a, K1b |
| 5. Metodología | Fuentes, validación, limitaciones | Texto y tabla |
 
---
 
## Modelo de tablas (Power BI, esquema estrella)
 
Regla: cada tabla de hechos tiene una sola granularidad ("una fila es…").
 
### Dimensiones
 
**dim_country**: `country_code` (PK), `country_name_es`, `country_name_en`
 
**dim_year**: `year` (PK, 1995–2025), `period` (pre_2008 1995–2007 / crisis_2008 2008–09 / between 2010–19 / covid 2020–21 / post_covid 2022–25), `comparison_period` (start 1995–97 / end 2022–24 / vacío), `crisis` (2008 / covid / vacío), `window` (before / during / after / vacío), `is_projection` (regla por verificar en ILOSTAT)
 
**dim_indicator**: `indicator_key` (PK: lfp, unemployment, epr, vulnerable, q, agriculture, industry, services), `name_es`, `block` (acceso / calidad / sector / síntesis), `unit` (%), `base` (población 15+ / fuerza laboral / ocupados), `wdi_code_female`, `wdi_code_male`, `source` (wdi / calculado)
 
### Hechos (calculados en Python)
 
**fact_indicator** — una fila = un indicador, un sexo, un país, un año: `country_code`, `year`, `indicator_key`, `sex` (female / male), `value`
→ A1, C1, C2a, K1 (niveles por sexo). Incluye epr y q calculados.
 
**fact_gap** — una fila = una brecha, un país, un año: `country_code`, `year`, `metric` (epr_gap / vulnerable_gap / q_gap / duncan_index), `value` (con signo: positivo = desventaja de las mujeres), `unit` (pp / %)
→ C2b, línea de referencia de K1, títulos y frases. Sin columna de signo aparte: el signo ya está en `value` y se deriva con SIGN() si hace falta.
 
**fact_decomposition** — una fila = una parte de una brecha, un país, un año: `country_code`, `year`, `decomposition` (epr_2parts / q_2parts / q_3parts), `component` (participation / unemployment / access / quality), `value_pp` (tamaño de la parte en pp, con signo), `share_pct` (% que representa esa parte de la brecha; las partes de una misma descomposición suman 100)
→ A2 (share_pct), S1 (value_pp). Control (suma de componentes = brecha) validado en Python antes de exportar.
 
Relaciones: cada fact → dim_country (country_code), dim_year (year); fact_indicator → dim_indicator (indicator_key).
 
Promedios por periodo y ventanas de crisis: medidas DAX usando `comparison_period`, `crisis` y `window` de dim_year (y un resumen en Python para validar y escribir los hallazgos).
 