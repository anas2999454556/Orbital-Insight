import { useEffect, useMemo, useState } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { Line, OrbitControls, Stars } from '@react-three/drei'
import { Minus, Plus } from 'lucide-react'
import * as THREE from 'three'
import usePrefersReducedMotion from '../../lib/usePrefersReducedMotion.js'
import { fetchGeometry } from '../../lib/api.js'

const MOON_RADIUS = 2
const MIN_DISTANCE = 8
const MAX_DISTANCE = 18
const START_DISTANCE = 12.5
const CAMERA_TILT_DEG = 34

const DEFAULT_SITE = { lon_deg: 222.51045, lat_deg: -89.46316 }
const DEFAULT_SITE_ID = 'site01'

function localFrame(lonDeg, latDeg) {
  const lon = THREE.MathUtils.degToRad(lonDeg)
  const lat = THREE.MathUtils.degToRad(latDeg)
  const cosLat = Math.cos(lat)

  const position = new THREE.Vector3(
    MOON_RADIUS * cosLat * Math.cos(lon),
    MOON_RADIUS * Math.sin(lat),
    -MOON_RADIUS * cosLat * Math.sin(lon),
  )
  const up = position.clone().normalize()
  const north = new THREE.Vector3(
    -Math.sin(lat) * Math.cos(lon),
    Math.cos(lat),
    Math.sin(lat) * Math.sin(lon),
  ).normalize()
  const east = new THREE.Vector3(
    -cosLat * Math.sin(lon),
    0,
    -cosLat * Math.cos(lon),
  ).normalize()

  return { position, up, north, east }
}

function directionFor(frame, azimuthDeg, elevationDeg) {
  const azimuth = THREE.MathUtils.degToRad(azimuthDeg)
  const elevation = THREE.MathUtils.degToRad(elevationDeg)
  const horizontal = Math.cos(elevation)

  return frame.east
    .clone()
    .multiplyScalar(horizontal * Math.sin(azimuth))
    .add(frame.north.clone().multiplyScalar(horizontal * Math.cos(azimuth)))
    .add(frame.up.clone().multiplyScalar(Math.sin(elevation)))
    .normalize()
}

function mulberry32(seed) {
  return function next() {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let value = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    value = (value + Math.imul(value ^ (value >>> 7), 61 | value)) ^ value
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296
  }
}

function createMoonTexture() {
  const width = 1024
  const height = 512
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  const random = mulberry32(20261113)

  ctx.fillStyle = '#90939a'
  ctx.fillRect(0, 0, width, height)

  for (let i = 0; i < 26; i += 1) {
    const x = random() * width
    const y = random() * height
    const radius = 40 + random() * 130
    const patch = ctx.createRadialGradient(x, y, 0, x, y, radius)
    patch.addColorStop(0, 'rgba(58, 62, 70, 0.34)')
    patch.addColorStop(1, 'rgba(58, 62, 70, 0)')
    ctx.fillStyle = patch
    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fill()
  }

  for (let i = 0; i < 420; i += 1) {
    const x = random() * width
    const y = random() * height
    const radius = 1.5 + random() * random() * 22

    ctx.fillStyle = `rgba(40, 43, 48, ${0.12 + random() * 0.22})`
    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fill()

    ctx.strokeStyle = `rgba(212, 216, 222, ${0.1 + random() * 0.18})`
    ctx.lineWidth = Math.max(1, radius * 0.18)
    ctx.beginPath()
    ctx.arc(x, y, radius * 0.9, Math.PI * 0.15, Math.PI * 0.75)
    ctx.stroke()
  }

  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  texture.anisotropy = 4
  return texture
}

function createGlowTexture() {
  const size = 256
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')
  const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  gradient.addColorStop(0, 'rgba(255, 250, 232, 1)')
  gradient.addColorStop(0.18, 'rgba(255, 226, 156, 0.72)')
  gradient.addColorStop(0.48, 'rgba(255, 186, 96, 0.22)')
  gradient.addColorStop(1, 'rgba(255, 170, 70, 0)')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, size, size)
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  return texture
}

function Moon() {
  const texture = useMemo(() => createMoonTexture(), [])

  return (
    <mesh>
      <sphereGeometry args={[MOON_RADIUS, 96, 96]} />
      <meshStandardMaterial
        map={texture}
        bumpMap={texture}
        bumpScale={0.03}
        roughness={0.95}
        metalness={0}
      />
    </mesh>
  )
}

function Marker({ direction, frame, color, opacity = 0.4, dashed = true, children }) {
  const position = useMemo(
    () => frame.position.clone().add(direction.clone().multiplyScalar(3.4)),
    [direction, frame],
  )

  return (
    <group>
      <Line
        points={[frame.position.toArray(), position.toArray()]}
        color={color}
        transparent
        opacity={opacity}
        lineWidth={1}
        dashed={dashed}
        dashSize={0.12}
        gapSize={0.1}
      />
      <group position={position}>{children}</group>
    </group>
  )
}

function SunMarker({ direction, frame, visible = true }) {
  const glow = useMemo(() => createGlowTexture(), [])

  return (
    <Marker direction={direction} frame={frame} color="#ffd27a" opacity={visible ? 0.4 : 0.15} dashed={!visible}>
      <sprite scale={[1.9, 1.9, 1]}>
        <spriteMaterial
          map={glow}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          transparent
          opacity={visible ? 1 : 0.25}
        />
      </sprite>
      <mesh>
        <sphereGeometry args={[0.16, 32, 32]} />
        <meshBasicMaterial color="#fff6df" transparent opacity={visible ? 1 : 0.35} />
      </mesh>
    </Marker>
  )
}

function EarthMarker({ direction, frame, visible = true }) {
  return (
    <Marker direction={direction} frame={frame} color="#6fa8d8" opacity={visible ? 0.4 : 0.18} dashed={!visible}>
      <mesh>
        <sphereGeometry args={[0.34, 48, 48]} />
        <meshStandardMaterial
          color="#2f6fb5"
          emissive="#0d2a4d"
          emissiveIntensity={visible ? 0.9 : 0.3}
          roughness={0.85}
          metalness={0}
          transparent
          opacity={visible ? 1 : 0.45}
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.38, 32, 32]} />
        <meshBasicMaterial
          color="#8fc4ff"
          transparent
          opacity={visible ? 0.18 : 0.06}
          side={THREE.BackSide}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </Marker>
  )
}

function CameraRig({ direction, distance }) {
  const camera = useThree((state) => state.camera)
  const controls = useThree((state) => state.controls)

  useEffect(() => {
    camera.position.copy(direction).normalize().multiplyScalar(distance)
    camera.up.set(0, 1, 0)
    controls?.update()
  }, [camera, controls, direction, distance])

  return null
}

function Scene({ frame, live, distance }) {
  const sunDirection = useMemo(
    () =>
      live?.sun
        ? directionFor(frame, live.sun.azimuth_deg, live.sun.elevation_deg)
        : null,
    [frame, live],
  )
  const earthDirection = useMemo(
    () =>
      live?.earth
        ? directionFor(frame, live.earth.azimuth_deg, live.earth.elevation_deg)
        : null,
    [frame, live],
  )

  const sunUp = (live?.sun?.elevation_deg ?? -90) > 0
  const lightPosition = sunDirection
    ? frame.position.clone().add(sunDirection.clone().multiplyScalar(20))
    : new THREE.Vector3(0, 20, 0)

  const cameraDirection = useMemo(() => {
    const tilt = THREE.MathUtils.degToRad(CAMERA_TILT_DEG)
    return frame.up
      .clone()
      .multiplyScalar(Math.cos(tilt))
      .add(frame.north.clone().multiplyScalar(Math.sin(tilt)))
      .normalize()
  }, [frame])

  return (
    <>
      <ambientLight intensity={sunUp ? 0.12 : 0.04} />
      <directionalLight
        position={lightPosition}
        intensity={sunUp ? 2.6 : 0.1}
        color="#fff2dc"
      />
      <Stars
        radius={70}
        depth={30}
        count={1800}
        factor={3}
        saturation={0}
        fade
        speed={0.4}
      />
      <Moon />
      {sunDirection && (
        <SunMarker direction={sunDirection} frame={frame} visible={sunUp} />
      )}
      {earthDirection && (
        <EarthMarker
          direction={earthDirection}
          frame={frame}
          visible={live?.earth?.visible_now ?? false}
        />
      )}
      <CameraRig direction={cameraDirection} distance={distance} />
    </>
  )
}

function Readout({ live }) {
  if (!live) {
    return (
      <div className="pointer-events-none absolute right-4 top-4 border border-line bg-void/80 px-3 py-2 font-mono text-xs text-ink-faint">
        Reading ephemeris…
      </div>
    )
  }

  const rows = [
    {
      key: 'Sun',
      body: live.sun,
      color: '#ffd27a',
      note:
        live.sun.elevation_deg > 0
          ? 'above the horizon'
          : 'below the horizon, site is in shadow',
    },
    {
      key: 'Earth',
      body: live.earth,
      color: '#6fa8d8',
      note: live.earth.visible_now ? 'in view' : 'below the horizon',
    },
  ]

  return (
    <div className="pointer-events-none absolute right-4 top-4 space-y-3 border border-line bg-void/85 px-3 py-2 font-mono text-xs">
      {rows.map((row) => (
        <div key={row.key}>
          <div className="flex items-center gap-2 uppercase tracking-[0.14em] text-ink-muted">
            <span className="h-2 w-2 rounded-full" style={{ background: row.color }} aria-hidden="true" />
            {row.key}
          </div>
          <div className="mt-1 text-ink">
            az {row.body.azimuth_deg.toFixed(1)}° · el {row.body.elevation_deg.toFixed(1)}°
          </div>
          <div className="text-ink-faint">{row.note}</div>
        </div>
      ))}
      <div className="border-t border-line pt-2 uppercase tracking-[0.14em] text-accent">
        derived · spice
      </div>
    </div>
  )
}

export default function MoonScene({ site = null, measurements = null }) {
  const reducedMotion = usePrefersReducedMotion()
  const [fetched, setFetched] = useState(null)
  const [distance, setDistance] = useState(START_DISTANCE)

  const live = measurements ?? fetched

  const activeSite = site ?? DEFAULT_SITE
  const frame = useMemo(
    () => localFrame(activeSite.lon_deg, activeSite.lat_deg),
    [activeSite],
  )

  useEffect(() => {
    if (measurements) return undefined
    let cancelled = false
    const utc = new Date().toISOString()
    fetchGeometry(DEFAULT_SITE_ID, utc, 1)
      .then((payload) => {
        if (!cancelled) setFetched(payload)
      })
      .catch(() => {
        if (!cancelled) setFetched(null)
      })
    return () => {
      cancelled = true
    }
  }, [measurements])

  const zoom = (step) => {
    setDistance((current) =>
      Math.min(MAX_DISTANCE, Math.max(MIN_DISTANCE, current + step)),
    )
  }

  return (
    <div className="relative">
      <div className="relative h-[360px] border border-line bg-surface sm:h-[440px] lg:h-[520px]">
        <Canvas
          camera={{ position: [0, 1.2, START_DISTANCE], fov: 42 }}
          dpr={[1, 2]}
          gl={{ antialias: true, alpha: true }}
        >
          <Scene frame={frame} live={live} distance={distance} />
          <OrbitControls
            enableZoom={false}
            enablePan={false}
            autoRotate={!reducedMotion}
            autoRotateSpeed={0.5}
            minPolarAngle={Math.PI * 0.25}
            maxPolarAngle={Math.PI * 0.65}
          />
        </Canvas>

        <div className="pointer-events-none absolute left-4 top-4 font-mono text-xs uppercase tracking-[0.14em] text-ink-faint">
          Live geometry preview
        </div>

        <Readout live={live} />

        <div className="absolute bottom-4 right-4 flex gap-2">
          <button
            type="button"
            onClick={() => zoom(-0.8)}
            aria-label="Zoom in"
            className="flex h-9 w-9 items-center justify-center border border-line-strong bg-void/80 text-ink-muted transition-colors duration-150 hover:border-accent hover:text-accent"
          >
            <Plus size={16} />
          </button>
          <button
            type="button"
            onClick={() => zoom(0.8)}
            aria-label="Zoom out"
            className="flex h-9 w-9 items-center justify-center border border-line-strong bg-void/80 text-ink-muted transition-colors duration-150 hover:border-accent hover:text-accent"
          >
            <Minus size={16} />
          </button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-ink-muted">
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#ffd27a]" aria-hidden="true" />
          Sun
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#6fa8d8]" aria-hidden="true" />
          Earth
        </span>
        <span className="text-ink-faint">Drag to rotate. Buttons to zoom.</span>
      </div>
      <p className="mt-2 max-w-xl text-xs text-ink-faint">
        Positions come from the SPICE ephemeris for the site and instant shown.
        Markers sit at the true direction from the site, so the Sun and the
        Earth only clear the local horizon when their elevation is positive.
      </p>
    </div>
  )
}
