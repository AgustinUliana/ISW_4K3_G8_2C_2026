// Unico lugar donde se usa la libreria "liquid-glass-react" (efecto Liquid Glass de Apple).
//
// La libreria dibuja un elemento que se posiciona solo (se centra con top/left 50% y un translate),
// pensado para flotar. Para usarlo como fondo de paneles y formularios, el contenido real queda en
// el flujo normal de la pagina y el vidrio se dibuja como una CAPA detras, del mismo tamaño que
// medimos del contenido. Asi los formularios se comportan como siempre.
//
// Su mapa de refraccion es cuadrado: funciona bien en elementos de proporcion parecida (tarjetas) y
// deja un contorno interior en los muy anchos (paneles, encabezado). Por eso esos usan refractar=false.
// En Safari y Firefox la refraccion no se ve (lo avisa la libreria): queda el vidrio esmerilado
// que da el CSS (.vidrio en estilos.css). Si no se puede medir, tambien queda solo el CSS.
import LiquidGlass from "liquid-glass-react";
import { useLayoutEffect, useRef, useState } from "react";

// El mapa de refraccion de la libreria es un cuadrado de 256x256: en elementos mas anchos que esto
// queda desalineado y se ve un contorno interior. Ahi alcanza con el vidrio esmerilado del CSS.
const PROPORCION_MAXIMA = 1.6;

export function Vidrio({
  children,
  className = "",
  radio = 28,
  elasticidad = 0, // 0 = no se mueve con el mouse (importante en formularios)
  refraccion = 40, // la libreria esta pensada para elementos chicos: en paneles grandes conviene menos
  refractar = true, // false = solo vidrio esmerilado (CSS): para paneles anchos, donde la libreria no alinea bien
  alClick,
}) {
  const contenedor = useRef(null);
  const [medida, setMedida] = useState(null);

  useLayoutEffect(() => {
    const elemento = contenedor.current;
    if (!refractar || !elemento || typeof ResizeObserver === "undefined") return undefined;
    const medir = () => setMedida({ ancho: elemento.offsetWidth, alto: elemento.offsetHeight });
    const observador = new ResizeObserver(medir);
    observador.observe(elemento);
    return () => observador.disconnect();
  }, [refractar]);

  return (
    <div
      ref={contenedor}
      className={`vidrio ${className}`.trim()}
      style={{ borderRadius: radio }}
      onClick={alClick}
    >
      {refractar && cabeLaRefraccion(medida) && (
        <div className="vidrio-capa" aria-hidden="true">
          <LiquidGlass
            cornerRadius={radio}
            padding="0px"
            elasticity={elasticidad}
            displacementScale={refraccion}
            blurAmount={0.12}
            saturation={125}
            aberrationIntensity={1.2}
            overLight={false}
            style={{ position: "absolute", top: "50%", left: "50%" }}
          >
            <div style={{ width: medida.ancho, height: medida.alto }} />
          </LiquidGlass>
        </div>
      )}
      <div className="vidrio-contenido">{children}</div>
    </div>
  );
}

function cabeLaRefraccion(medida) {
  if (!medida || medida.ancho <= 0 || medida.alto <= 0) return false;
  return medida.ancho / medida.alto <= PROPORCION_MAXIMA;
}
