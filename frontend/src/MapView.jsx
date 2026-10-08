import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  GeoJSON
} from "react-leaflet";

import "leaflet/dist/leaflet.css";


function MapView() {

  const [parcels, setParcels] = useState(null);
  const [conflicts, setConflicts] = useState([]);


  // -----------------------------------------
  // LOAD GIS PARCELS
  // -----------------------------------------

  useEffect(() => {

    fetch("/sample_parcels.geojson")
      .then((response) => {

        if (!response.ok) {
          throw new Error("Unable to load GIS parcel data");
        }

        return response.json();

      })
      .then((data) => {
        setParcels(data);
      })
      .catch((error) => {

        console.error(
          "Unable to load parcel geometry:",
          error
        );

      });

  }, []);


  // -----------------------------------------
  // LOAD CONFLICT DATA
  // -----------------------------------------

  useEffect(() => {

    fetch("http://127.0.0.1:8000/conflicts")
      .then((response) => {

        if (!response.ok) {
          throw new Error("Unable to load conflict data");
        }

        return response.json();

      })
      .then((data) => {

        setConflicts(
          Array.isArray(data.conflicts)
            ? data.conflicts
            : []
        );

      })
      .catch((error) => {

        console.error(
          "Unable to load conflict data:",
          error
        );

      });

  }, []);


  // -----------------------------------------
  // FIND PARCEL CONFLICT
  // -----------------------------------------

  const getParcelConflict = (parcelId) => {

  const normalizedParcelId =
    String(parcelId).trim().toUpperCase();

  return conflicts.find(
    (conflict) =>
      String(conflict.parcel_id)
        .trim()
        .toUpperCase() === normalizedParcelId
  );

};

  // -----------------------------------------
  // RISK COLOR
  // -----------------------------------------

  const getParcelColor = (parcelId) => {

    const conflict =
      getParcelConflict(parcelId);


    if (!conflict) {
      return "#94a3b8";
    }


    switch (conflict.risk_level) {

      case "HIGH":
        return "#ef4444";

      case "MEDIUM":
        return "#f59e0b";

      case "LOW":
        return "#22c55e";

      default:
        return "#94a3b8";
    }

  };


  // -----------------------------------------
  // PARCEL STYLE
  // -----------------------------------------

  const parcelStyle = (feature) => {

    const parcelId =
      feature.properties.parcel_id;


    const color =
      getParcelColor(parcelId);


    return {

      color: color,

      weight: 3,

      fillColor: color,

      fillOpacity: 0.40

    };

  };


  // -----------------------------------------
  // PARCEL POPUP
  // -----------------------------------------

  const onEachParcel = (
    feature,
    layer
  ) => {

    const parcelId =
      feature.properties.parcel_id;

    const village =
      feature.properties.village;


    const conflict =
      getParcelConflict(parcelId);


    // -----------------------------------------
    // NO CONFLICT
    // -----------------------------------------

    if (!conflict) {

      layer.bindPopup(`

        <div style="
          min-width:220px;
          font-family:Arial,sans-serif;
        ">

          <div style="
            font-size:16px;
            font-weight:700;
            margin-bottom:8px;
          ">
            Parcel ${parcelId}
          </div>

          <div>
            <strong>Village:</strong>
            ${village}
          </div>

          <hr/>

          <div style="
            color:#16a34a;
            font-weight:600;
          ">
            ✓ No conflict detected
          </div>

        </div>

      `);

      return;
    }


    // -----------------------------------------
    // CONFLICT POPUP
    // -----------------------------------------

    const riskColor =
      getParcelColor(parcelId);


    layer.bindPopup(`

      <div style="
        min-width:250px;
        font-family:Arial,sans-serif;
      ">

        <div style="
          font-size:17px;
          font-weight:700;
          margin-bottom:8px;
        ">
          Parcel ${parcelId}
        </div>


        <div style="
          margin-bottom:8px;
        ">

          <strong>Village:</strong>
          ${village}

        </div>


        <div style="
          padding:8px;
          border-radius:6px;
          background:${riskColor};
          color:white;
          font-weight:700;
          text-align:center;
          margin-bottom:10px;
        ">

          ${conflict.risk_level} RISK

        </div>


        <div style="line-height:1.7;">

          <strong>Confidence:</strong>
          ${conflict.confidence ?? "N/A"}%

          <br/>

          <strong>Status:</strong>
          ${conflict.status ?? "N/A"}

          <hr/>


          <strong>Area Difference:</strong>
          ${conflict.area_difference_percentage ?? "N/A"}%

          <br/>

          <strong>Boundary Deviation:</strong>
          ${conflict.boundary_deviation_m ?? "N/A"} m

          <br/>

          <strong>GNSS Accuracy:</strong>
          ${conflict.gnss_accuracy_cm ?? "N/A"} cm

        </div>

      </div>

    `);

  };


  // -----------------------------------------
  // MAP
  // -----------------------------------------

  return (

    <div
      className="map-wrapper"
      style={{
        position: "relative"
      }}
    >

      <MapContainer

        center={[
          11.0175,
          76.9575
        ]}

        zoom={16}

        scrollWheelZoom={true}

        className="land-map"
      >


        <TileLayer

          attribution="
            &copy; OpenStreetMap contributors
          "

          url="
            https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
          "

        />


        {parcels && (

          <GeoJSON

            data={parcels}

            style={parcelStyle}

            onEachFeature={onEachParcel}

          />

        )}


      </MapContainer>


      {/* -------------------------------------
          MAP LEGEND
      ------------------------------------- */}

      <div
        style={{
          position: "absolute",
          bottom: "20px",
          right: "20px",
          background: "white",
          padding: "14px 16px",
          borderRadius: "10px",
          boxShadow: "0 4px 15px rgba(0,0,0,0.18)",
          zIndex: 1000,
          fontSize: "13px",
          minWidth: "150px"
        }}
      >

        <div
          style={{
            fontWeight: "700",
            marginBottom: "10px"
          }}
        >
          Risk Level
        </div>


        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginBottom: "6px"
        }}>

          <span style={{
            width: "13px",
            height: "13px",
            background: "#ef4444",
            borderRadius: "3px"
          }} />

          HIGH

        </div>


        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginBottom: "6px"
        }}>

          <span style={{
            width: "13px",
            height: "13px",
            background: "#f59e0b",
            borderRadius: "3px"
          }} />

          MEDIUM

        </div>


        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginBottom: "6px"
        }}>

          <span style={{
            width: "13px",
            height: "13px",
            background: "#22c55e",
            borderRadius: "3px"
          }} />

          LOW

        </div>


        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>

          <span style={{
            width: "13px",
            height: "13px",
            background: "#94a3b8",
            borderRadius: "3px"
          }} />

          NO CONFLICT

        </div>

      </div>


    </div>

  );

}


export default MapView;