// Unico lugar donde se usa la libreria "liquid-glass-react" (efecto Liquid Glass de Apple).
// Si en el futuro se cambia de libreria, solo se toca este archivo. En Safari y Firefox la
// refraccion no se ve (lo avisa la libreria) y queda el vidrio esmerilado (desenfoque).
import LiquidGlass from "liquid-glass-react";

export function Vidrio({
  children,
  className = "",
  radio = 28,
  relleno = "0px",
  elasticidad = 0, // 0 = el panel no se mueve con el mouse (importante en formularios)
  alClick,
}) {
  return (
    <LiquidGlass
      className={`vidrio ${className}`.trim()}
      cornerRadius={radio}
      padding={relleno}
      elasticity={elasticidad}
      displacementScale={52}
      blurAmount={0.12}
      saturation={125}
      aberrationIntensity={1.2}
      overLight={false}
      onClick={alClick}
    >
      {children}
    </LiquidGlass>
  );
}
