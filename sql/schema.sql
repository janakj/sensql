--
-- PostgreSQL database dump
--

-- Dumped from database version 13.5 (Debian 13.5-1.pgdg100+1)
-- Dumped by pg_dump version 13.5 (Debian 13.5-1.pgdg100+1)

-- Started on 2021-12-03 09:46:06 EST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3902 (class 1262 OID 154265)
-- Name: geonaming; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE geonaming WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';


ALTER DATABASE geonaming OWNER TO postgres;

\connect geonaming

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 154267)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 3903 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- TOC entry 3 (class 3079 OID 155282)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 3904 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 1383 (class 1247 OID 155294)
-- Name: feature_t; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.feature_t AS ENUM (
    'Area',
    'Building',
    'Floor',
    'Apartment',
    'Room',
    'Way',
    'Point'
);


ALTER TYPE public.feature_t OWNER TO postgres;

--
-- TOC entry 932 (class 1255 OID 155389)
-- Name: find_shape(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.find_shape(feature_id uuid) RETURNS uuid
    LANGUAGE plpgsql
    AS $$
begin
    return (
        with recursive parent as (
            select id, shape from feature
            union all
            select f.id as id, p.shape
                from feature as f, parent as p
                where f.parent = p.id)
            select shape from feature
            where feature.id = feature_id
            and shape is not null
        union all
            select parent.shape
            from feature, parent
            where
                feature.id = feature_id
                and feature.parent = parent.id
                and parent.shape is not null
        limit 1
    );
end;
$$;


ALTER FUNCTION public.find_shape(feature_id uuid) OWNER TO postgres;

--
-- TOC entry 934 (class 1255 OID 155391)
-- Name: projective_transform(double precision[], double precision[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.projective_transform(matrix double precision[], coordinates double precision[]) RETURNS double precision[]
    LANGUAGE plpgsql
    AS $_$
declare
    d double precision;
begin
    -- FIXME: Handle potential division by zero
    d := $1[3][1] * $2[1] + $1[3][2] * $2[2] + $1[3][3];
    return array [
        ($1[1][1] * $2[1] + $1[1][2] * $2[2] + $1[1][3]) / d,
        ($1[2][1] * $2[1] + $1[2][2] * $2[2] + $1[2][3]) / d
    ];
end;
$_$;


ALTER FUNCTION public.projective_transform(matrix double precision[], coordinates double precision[]) OWNER TO postgres;

--
-- TOC entry 933 (class 1255 OID 155390)
-- Name: uncertainty_circle(public.geometry, real); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uncertainty_circle(center public.geometry, radius real) RETURNS public.geometry
    LANGUAGE plpgsql
    AS $$
begin
    if radius is null then
        return center;
    else
        -- Transform the center point to WebMercator so that we can create a
        -- buffer for with with a radius value in meters. Then transform the
        -- resulting polygon back to 4326
        return
            st_transform(st_buffer(st_transform(center, 900913), radius), 4326);
    end if;
end;
$$;


ALTER FUNCTION public.uncertainty_circle(center public.geometry, radius real) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 209 (class 1259 OID 155344)
-- Name: control_point; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.control_point (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    coordinates public.geometry(Point)
);


ALTER TABLE public.control_point OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 155355)
-- Name: coordinate_transform; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coordinate_transform (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    control_links jsonb NOT NULL
);


ALTER TABLE public.coordinate_transform OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 155378)
-- Name: device; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.device (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    center public.geometry(Point),
    radius real
);


ALTER TABLE public.device OWNER TO postgres;

--
-- TOC entry 213 (class 1259 OID 155448)
-- Name: device_shape; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.device_shape (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    device_id uuid NOT NULL,
    shape_id uuid NOT NULL
);


ALTER TABLE public.device_shape OWNER TO postgres;

--
-- TOC entry 208 (class 1259 OID 155320)
-- Name: feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    type public.feature_t,
    name text NOT NULL,
    parent uuid,
    vertical_range text,
    indoor boolean DEFAULT true,
    shape uuid,
    control_points text[],
    created timestamp with time zone DEFAULT now() NOT NULL,
    image text,
    transform text,
    attrs jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE public.feature OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 155366)
-- Name: raster_image; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.raster_image (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    url text NOT NULL,
    uploaded timestamp with time zone DEFAULT now() NOT NULL,
    last_modified timestamp with time zone,
    width integer NOT NULL,
    height integer NOT NULL,
    size integer NOT NULL,
    file_name text NOT NULL,
    storage_ref text NOT NULL
);


ALTER TABLE public.raster_image OWNER TO postgres;

--
-- TOC entry 207 (class 1259 OID 155309)
-- Name: shape; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shape (
    uid text DEFAULT current_setting('session.uid'::text) NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    geometries public.geometry(GeometryCollection) NOT NULL
);


ALTER TABLE public.shape OWNER TO postgres;

--
-- TOC entry 3738 (class 2606 OID 155353)
-- Name: control_point control_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_point
    ADD CONSTRAINT control_point_pkey PRIMARY KEY (id);


--
-- TOC entry 3740 (class 2606 OID 155364)
-- Name: coordinate_transform coordinate_transform_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coordinate_transform
    ADD CONSTRAINT coordinate_transform_pkey PRIMARY KEY (id);


--
-- TOC entry 3744 (class 2606 OID 155387)
-- Name: device device_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_pkey PRIMARY KEY (id);


--
-- TOC entry 3746 (class 2606 OID 155456)
-- Name: device_shape device_shape_device_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_shape
    ADD CONSTRAINT device_shape_device_id_key UNIQUE (device_id);


--
-- TOC entry 3736 (class 2606 OID 155332)
-- Name: feature feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_pkey PRIMARY KEY (id);


--
-- TOC entry 3742 (class 2606 OID 155376)
-- Name: raster_image raster_image_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raster_image
    ADD CONSTRAINT raster_image_pkey PRIMARY KEY (id);


--
-- TOC entry 3734 (class 2606 OID 155318)
-- Name: shape shape_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shape
    ADD CONSTRAINT shape_pkey PRIMARY KEY (id);


--
-- TOC entry 3747 (class 2606 OID 155333)
-- Name: feature feature_parent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_parent_fkey FOREIGN KEY (parent) REFERENCES public.feature(id);


--
-- TOC entry 3748 (class 2606 OID 155338)
-- Name: feature feature_shape_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_shape_fkey FOREIGN KEY (shape) REFERENCES public.shape(id) ON DELETE SET NULL;


--
-- TOC entry 3886 (class 0 OID 155344)
-- Dependencies: 209
-- Name: control_point; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.control_point ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 3892 (class 3256 OID 155354)
-- Name: control_point control_point_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY control_point_policy ON public.control_point USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3887 (class 0 OID 155355)
-- Dependencies: 210
-- Name: coordinate_transform; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.coordinate_transform ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 3893 (class 3256 OID 155365)
-- Name: coordinate_transform coordinate_transform_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY coordinate_transform_policy ON public.coordinate_transform USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3889 (class 0 OID 155378)
-- Dependencies: 212
-- Name: device; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.device ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 3895 (class 3256 OID 155388)
-- Name: device device_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY device_policy ON public.device USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3896 (class 3256 OID 155457)
-- Name: device_shape device_shape_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY device_shape_policy ON public.device_shape USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3885 (class 0 OID 155320)
-- Dependencies: 208
-- Name: feature; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.feature ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 3891 (class 3256 OID 155343)
-- Name: feature feature_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY feature_policy ON public.feature USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3888 (class 0 OID 155366)
-- Dependencies: 211
-- Name: raster_image; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.raster_image ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 3894 (class 3256 OID 155377)
-- Name: raster_image raster_image_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY raster_image_policy ON public.raster_image USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3884 (class 0 OID 155309)
-- Dependencies: 207
-- Name: shape; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.shape ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 3890 (class 3256 OID 155319)
-- Name: shape shape_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY shape_policy ON public.shape USING ((uid = current_setting('session.uid'::text))) WITH CHECK ((uid = current_setting('session.uid'::text)));


--
-- TOC entry 3905 (class 0 OID 0)
-- Dependencies: 209
-- Name: TABLE control_point; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.control_point TO geo_api;


--
-- TOC entry 3906 (class 0 OID 0)
-- Dependencies: 210
-- Name: TABLE coordinate_transform; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.coordinate_transform TO geo_api;


--
-- TOC entry 3907 (class 0 OID 0)
-- Dependencies: 212
-- Name: TABLE device; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.device TO geo_api;


--
-- TOC entry 3908 (class 0 OID 0)
-- Dependencies: 213
-- Name: TABLE device_shape; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.device_shape TO geo_api;


--
-- TOC entry 3909 (class 0 OID 0)
-- Dependencies: 208
-- Name: TABLE feature; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.feature TO geo_api;


--
-- TOC entry 3910 (class 0 OID 0)
-- Dependencies: 211
-- Name: TABLE raster_image; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.raster_image TO geo_api;


--
-- TOC entry 3911 (class 0 OID 0)
-- Dependencies: 207
-- Name: TABLE shape; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.shape TO geo_api;


-- Completed on 2021-12-03 09:46:07 EST

--
-- PostgreSQL database dump complete
--

