CREATE OR REPLACE FUNCTION prep(text) RETURNS text
    AS $$ SELECT
		REPLACE(
			REPLACE(
				REPLACE(
					UPPER(
                        REPLACE(
                            REPLACE(
                                REPLACE($1,'ß','ss')
                            ,' ','')
                        ,'-','')
					)
				,'Ä','AE')
			,'Ö','OE')
		,'Ü','UE');
		$$
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

DROP VIEW IF EXISTS  gws_adressen_no_plz;
CREATE VIEW gws_adressen_no_plz AS
SELECT
    prep(gm.bezeichnung) AS gemeinde,
    prep(ka.bezeichnung) AS strasse,
    prep(lb.hausnummer) AS hausnummer,
    ka.bezeichnung || ' ' || lb.hausnummer AS str_nr,
    ge.wkb_geometry AS geom,
    st_x(st_centroid(ge.wkb_geometry)) as x,
    st_y(st_centroid(ge.wkb_geometry)) as y
FROM
    ax_lagebezeichnungkatalogeintrag AS ka,
    ax_lagebezeichnungmithausnummer AS lb,
    ax_gebaeude AS ge,
    ax_gemeinde AS gm
WHERE
    lb.endet IS NULL
    AND ARRAY[lb.gml_id] <@ ge.zeigtauf
    AND ge.endet IS NULL
    AND ka.kreis = lb.kreis
    AND ka.gemeinde = lb.gemeinde
    AND ka.lage = lb.lage
    AND ka.kreis = gm.kreis
    AND ka.gemeinde = gm.gemeinde
