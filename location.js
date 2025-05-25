navigator.geolocation.getCurrentPosition(
  (position) => {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const data = { lat: lat, lon: lon };
    window.parent.postMessage(data, "*");
  },
  (err) => {
    alert("Location access denied.");
  }
);
