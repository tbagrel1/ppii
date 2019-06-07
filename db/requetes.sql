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

#Retourne le vol le plus long à destination de New York

WITH t1 AS (
    SELECT Path.db_step_nb, Path.id, Path.straight_distance, AirportPath.airport_icao
    FROM Path
             JOIN AirportPath ON Path.id = AirportPath.path_id
    WHERE AirportPath.step_no = Path.db_step_nb - 1
      AND AirportPath.airport_icao IN
          (
              SELECT Airport.icao
              FROM Airport
              WHERE UPPER(Airport.city) = 'NEW YORK'
          )
)
SELECT t1.id, t1.straight_distance
FROM t1
INNER JOIN (
    SELECT MAX(t1.straight_distance) AS dist_max
    FROM t1
    ) t2
ON t2.dist_max = t1.straight_distance

#Retourne le vol le plus court à destination de New York

WITH t1 AS (
    SELECT Path.db_step_nb, Path.id, Path.straight_distance, AirportPath.airport_icao
    FROM Path
             JOIN AirportPath ON Path.id = AirportPath.path_id
    WHERE AirportPath.step_no = Path.db_step_nb - 1
      AND AirportPath.airport_icao IN
          (
              SELECT Airport.icao
              FROM Airport
              WHERE UPPER(Airport.city) = 'NEW YORK'
          )
)
SELECT t1.id, t1.straight_distance
FROM t1
INNER JOIN (
    SELECT MIN(t1.straight_distance) AS dist_min
    FROM t1
    ) t2
ON t2.dist_min = t1.straight_distance
