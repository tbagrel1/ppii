# Retourne la Liste des aéroports dans un pays donné (ici France).
SELECT Airport.icao, Airport.name
FROM Airport
WHERE UPPER(Airport.country) = 'FRANCE'

#Retourne le vol avec les plus d'escales dans un même pays (ainsi que le nombre d'escale et le pays)

WITH t1 AS
(
SELECT AirportPath.path_id, Airport.country, COUNT(Airport.country) AS country_count
         FROM AirportPath
                  JOIN Airport ON Airport.icao = AirportPath.airport_icao
         GROUP BY AirportPath.path_id, Airport.country
)
SELECT t1.path_id, t1.country, t1.country_count
FROM t1
INNER JOIN
(
    SELECT MAX(t1.country_count) AS country_count_max
    FROM t1
) t2
ON t2.country_count_max = t1.country_count