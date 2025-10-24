function onScanSuccess(decodedText) {
    document.getElementById("result").innerText = "Scanning...";

    fetch("/scan_barcode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ barcode: decodedText })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById("result").innerText = data.error;
        } else {
            let color = data.status === "valid" ? "green" : "red";
            document.getElementById("result").innerHTML =
                `<b style="color:${color}">${data.name}</b><br>
                Expiry Date: ${data.expiry_date}<br>
                Status: ${data.status.toUpperCase()}`;
        }
    });
}

const html5QrCode = new Html5Qrcode("reader");
html5QrCode.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 250 },
    onScanSuccess
);
