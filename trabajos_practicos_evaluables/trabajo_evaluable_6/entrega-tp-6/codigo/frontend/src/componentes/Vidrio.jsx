// Unico lugar donde se usa la libreria "liquid-glass-react" (efecto Liquid Glass de Apple).
//
// La libreria dibuja un elemento que se posiciona solo (se centra con top/left 50% y un translate),
// pensado para flotar. Para usarlo como fondo de paneles y formularios, el contenido real queda en
// el flujo normal de la pagina y el vidrio se dibuja como una CAPA detras, del mismo tamaño que
// medimos del contenido. Asi los formularios se comportan como siempre.
//
// En Safari y Firefox la refraccion no se ve (lo avisa la libreria): queda el vidrio esmerilado
// que da el CSS (.vidrio en estilos.css). Si no se puede medir, tambien queda solo el CSS.
import LiquidGlass from "liquid-glass-react";
import { useLayoutEffect, useRef, useState } from "react";

export function Vidrio({
  children,
  className = "",
  radio = 28,
  elasticidad = 0, // 0 = no se mueve con el mouse (importante en formularios)
  alClick,
}) {
  const contenedor = useRef(null);
  const [medida, setMedida] = useState(null);

  useLayoutEffect(() => {
    const elemento = contenedor.current;
    if (!elemento || typeof ResizeObserver === "undefined") return undefined;
    const medir = () => setMedida({ ancho: elemento.offsetWidth, alto: elemento.offsetHeight });
    const observador = new ResizeObserver(medir);
    observador.observe(elemento);
    return () => observador.disconnect();
  }, []);

  return (
    <div
      ref={contenedor}
      className={`vidrio ${className}`.trim()}
      style={{ borderRadius: radio }}
      onClick={alClick}
    >
      {medida && medida.ancho > 0 && medida.alto > 0 && (
        <div className="vidrio-capa" aria-hidden="true">
          <LiquidGlass
            cornerRadius={radio}
            elasticity={elasticidad}
            displacementScale={52}
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
