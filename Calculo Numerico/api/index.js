var str_version_api = "api/v1/";

function crear_peticion(ruta, cuerpo, funcion) {
    var xhr = new XMLHttpRequest();
    xhr.open(cuerpo == null ? "GET" : "POST", ruta);
    xhr.onreadystatechange = funcion;
    return xhr;
}

app_conversion = new Vue({
    el: "#app-conversion-bases",
    data: {
        numero: "",
        desde: 2,
        a: 3,
        salida: "",
        bases: [2, 3, 8, 16]
    },
    methods: {
        calcular() {
            var ruta = str_version_api + "conversion-bases?";
            ruta += "numero=" + encodeURIComponent(this.numero);
            ruta += "&desde=" + this.desde;
            ruta += "&a=" + this.a;
            var xhr = crear_peticion(ruta, null, evento => {
                var xhr = evento.target;
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        this.salida = xhr.responseText;
                    } else if (xhr.status == 422) {
                        alert(JSON.parse(xhr.responseText).detail[0].msg);
                    }
                }
            });
            xhr.send();
        }
    }
});
