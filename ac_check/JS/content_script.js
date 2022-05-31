if(typeof init === 'undefined'){

	const init = function(){
		var main = document.getElementById('main_s');
		var loc = window.location.hostname;
		if(main === null && loc !== 'www.w3.org' && !loc.startsWith("chrome://")){
			//var bd = document.body.getElementsByTagName("*");
			var bd = document.querySelectorAll( 'body > *' );

			var ele = document.createElement('div');
			ele.setAttribute("id", "main_s");
			ele.setAttribute("class", "main_s");

			var side_nav = document.createElement('div');
			side_nav.setAttribute("id", "sidenav_s");
			side_nav.setAttribute("class", "sidenav_s");



			document.body.innerHTML = '';
			document.body.appendChild(ele);
			document.body.appendChild(side_nav);
			//document.getElementById('main_s').appendChilds(bd)
			for (let item of bd) {
				document.getElementById('main_s').appendChild(item)
			}
			/*
			let codigo_nav = '<input type="button" id="limpiar" name="limpiar" value="Limpiar datos&#x00A;almacenados" class="boton_secundario_sn"/><br><br><br>';
			codigo_nav+= '<input type="button" id="auto" name="auto" value="Obtener datos&#x00A;automáticamente" class="boton_principal_sn"/><br><br><br><br>';
			codigo_nav+= '<label class="boton_secundario_sn2"><input id="file-upload-button" type="file" style="display: none;" accept=".json"/>Agregar un informe</label><br><br><br>';
			codigo_nav+= '<input type="button" id="download" name="download" class="boton_principal_sn2" value="Descargar informe" /><br><br><br>';
			codigo_nav+= '<br><br><p class="titulo_sb">Contenido del informe:</p><p id="tabla_res"></p><br><br><p id="tabla_contenido"></p><script type="text/javascript" src="/JS/agregar_informes.js"></script><script type="text/javascript" src="http://127.0.0.1:5000/tablas.js"></script><script src="/JS/funciones_jquery.js"></script>';
			*/
			let codigo_nav = '<label id="limpiar" name="limpiar" class="boton_secundario_sn">Clean stored data</label><br><br>';
			codigo_nav+= '<label id="auto" name="auto" class="boton_principal_sn">Get automatically <br> generated report</label><br><br><br><br>';
			codigo_nav+= '<label class="boton_secundario_sn2"><input id="file-upload-button" type="file" style="display: none;" accept=".json"/>Upload a report</label><br><br><br>';
			codigo_nav+= '<label id="download" name="download" class="boton_principal_sn2">Download report</label><br><br><br>';
			codigo_nav+= '<br><br><p class="titulo_sb">&nbsp;<u>Report content</u>:</p><br><p id="tabla_res"></label><br><br><p id="tabla_contenido"></p><br><br><br><script type="text/javascript" src="/JS/agregar_informes.js"></script><script type="text/javascript" src="http://127.0.0.1:5000/tablas.js"></script><script src="/JS/funciones_jquery.js"></script>';
			document.getElementById('sidenav_s').innerHTML=codigo_nav;

		}else{
			console.log("Value"+String(main));
		}
		
	}

	init();
}
