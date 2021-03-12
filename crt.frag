#version 130

uniform float osg_FrameTime;
uniform sampler2D p3d_Texture0;
uniform sampler2D pattern;
uniform vec2 iResolution;

in vec4 vtx_color;
in vec2 texcoord;

out vec4 color;




// CRT Effect Pulled from : "[SIG15] Mario World 1-1" by Krzysztof Narkowicz @knarkowicz
//
//
#define SPRITE_DEC( x, i ) 	mod( floor( i / pow( 4.0, mod( x, 8.0 ) ) ), 4.0 )
#define SPRITE_DEC2( x, i ) mod( floor( i / pow( 4.0, mod( x, 11.0 ) ) ), 4.0 )
#define RGB( r, g, b ) vec3( float( r ) / 255.0, float( g ) / 255.0, float( b ) / 255.0 )

vec2 CRTCurveUV( vec2 uv )
{
    uv = uv * 2.0 - 1.0;
    vec2 offset = abs( uv.yx ) / vec2( 6.0, 4.0 );
    uv = uv + uv * offset * offset;
    uv = uv * 0.5 + 0.5;
    return uv;
}

vec3 DrawVignette( vec3 color, vec2 uv )
{
    float vignette = uv.x * uv.y * ( 1.0 - uv.x ) * ( 1.0 - uv.y );
    vignette = clamp( pow( 16.0 * vignette, 0.3 ), 0.0, 1.0 );
    color *= pow(vignette, 2.5);
    return color;
}

/*vec3 DrawScanline( vec3 color, vec2 uv )
{
    float scanline 	= clamp( 0.95 + 0.05 * cos( 3.14 * ( uv.y + 0.008 * osg_FrameTime ) * 240.0 * 1.0 ), 0.0, 1.0 );
    float grille 	= 0.85 + 0.15 * clamp( 1.5 * cos( 3.14 * uv.x * 640.0 * 1.0 ), 0.0, 1.0 );
    color *= scanline * grille * 1.2;
    return color;
}*/


void main()
{
    // we want to see at least 224x192 (overscan) and we want multiples of pixel size
    float resMultX  = floor( iResolution.x / 224.0 );
    float resMultY  = floor( iResolution.y / 192.0 );
    float resRcp	= 1.0 / max( min( resMultX, resMultY ), 1.0 );

    float time			= osg_FrameTime;
    float screenWidth	= floor( iResolution.x * resRcp );
    float screenHeight	= floor( iResolution.y * resRcp );
    float pixelX 		= floor( gl_FragCoord.x * resRcp );
    float pixelY 		= floor( gl_FragCoord.y * resRcp );

    //vec3 tmp_color = vtx_color.rgb * ;



    // CRT effects (curvature, vignette, scanlines and CRT grille)
    vec2 uv    = gl_FragCoord.xy / iResolution.xy;
    vec2 crtUV = CRTCurveUV( uv );
    uv = uv * 0.7 + crtUV * 0.3;

    vec3 pat = texture2D(pattern, (gl_FragCoord.xy - vec2(0, 0)) / (vec2(256, 256) * 0.005) + vec2(0, osg_FrameTime  * 0.5)).rgb;

    vec3 tmp_color = texture2D(p3d_Texture0, uv + (pat.xy - vec2(0.5, 0.5)) * 0.004).rgb
                   + texture2D(p3d_Texture0, uv + (pat.yz - vec2(0.5, 0.5)) * 0.004).rgb;
    if ( crtUV.x < 0.0 || crtUV.x > 1.0 || crtUV.y < 0.0 || crtUV.y > 1.0 )
    {
        tmp_color = vec3( 0.0 );
    }
    //tmp_color = DrawScanline( tmp_color, uv );

    tmp_color *= pat * 0.7;

    tmp_color += texture2D(p3d_Texture0, uv).rgb * 0.2;
    tmp_color = DrawVignette( tmp_color, uv );

	color 	= vec4( tmp_color, 1.0 );
    //gl_FragColor.w		= 1.0;
}
