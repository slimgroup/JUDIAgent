using JUDI, JLD2, PythonPlot, LinearAlgebra

# Improved compact RTM benchmark that preserves the original RTM workflow
# while adding a standard water-column mute to suppress shallow source imprint.

for dir in ["outputs/figures", "outputs/data"]
    isdir(dir) || mkpath(dir)
end

println("Setting up compact RTM benchmark with water-column mute...")

# ==============================================================================
# 1. Model setup - compact validation scale
# ==============================================================================

n = (201, 101)
d = (10f0, 10f0)
o = (0f0, 0f0)

v_true = ones(Float32, n) .* 1.5f0
for iz = 1:n[2]
    for ix = 1:n[1]
        interface_depth = 56
        if iz >= interface_depth
            v_true[ix, iz] = 2.0f0
        end
    end
end

v_mig = copy(v_true)
for iz = 2:n[2]-1
    for ix = 2:n[1]-1
        v_mig[ix, iz] = 0.2f0 * v_true[ix, iz] +
                        0.2f0 * (v_true[ix - 1, iz] + v_true[ix + 1, iz] +
                                 v_true[ix, iz - 1] + v_true[ix, iz + 1])
    end
end

m_true = (1f0 ./ v_true).^2
m_mig = (1f0 ./ v_mig).^2

model_true = Model(n, d, o, m_true)
model_mig = Model(n, d, o, m_mig)

println("Model: $n grid, $(d[1])m spacing")
println("True velocity: $(minimum(v_true))-$(maximum(v_true)) km/s")

# ==============================================================================
# 2. Acquisition geometry
# ==============================================================================

nsrc = 5
nrec = 100
shot_spacing = 250f0
receiver_spacing = 12f0

source_depth = 10f0
receiver_depth = 12f0

recording_time = 1800f0
dt = 4f0

xsrc = convertToCell(collect(150f0 .+ shot_spacing .* Float32.(0:nsrc-1)))
ysrc = convertToCell(fill(0f0, nsrc))
zsrc = convertToCell(fill(source_depth, nsrc))
dt_src = fill(dt, nsrc)
t_src = fill(recording_time, nsrc)
src_geometry = Geometry(xsrc, ysrc, zsrc; dt=dt_src, t=t_src)

xrec = collect(range(0f0, step=receiver_spacing, length=nrec))
yrec = fill(0f0, nrec)
zrec = fill(receiver_depth, nrec)
rec_geometry = Geometry(xrec, yrec, zrec; dt=dt, t=recording_time, nsrc=nsrc)

println("Acquisition: $nsrc sources, $nrec receivers")

# ==============================================================================
# 3. Source wavelet and observed data
# ==============================================================================

f0 = 0.015f0
wavelet = ricker_wavelet(recording_time, dt, f0)
q = judiVector(src_geometry, wavelet)

println("Generating synthetic data...")
F_true = judiModeling(model_true, src_geometry, rec_geometry)
d_obs = F_true * q

noise_level = 0.02f0
for i = 1:nsrc
    noise = randn(Float32, size(d_obs.data[i]))
    d_obs.data[i] .+= noise_level * maximum(abs.(d_obs.data[i])) * noise
end

# ==============================================================================
# 4. RTM computation
# ==============================================================================

println("Computing RTM...")
F_mig = judiModeling(model_mig, src_geometry, rec_geometry)
J = judiJacobian(F_mig, q)
rtm = adjoint(J) * d_obs
rtm_image_raw = reshape(rtm, n)

# Standard practice: mute the water column in the improved RTM image product
# while preserving the raw RTM image for comparison.
water_mute_depth_m = 120f0
mute_rows = min(n[2], max(0, floor(Int, water_mute_depth_m / d[2]) + 1))
rtm_image_muted = copy(rtm_image_raw)
if mute_rows > 0
    rtm_image_muted[:, 1:mute_rows] .= 0f0
end

println("RTM computed: size $(size(rtm_image_raw))")
println("Applied water-column mute to top $(mute_rows) rows (~$(mute_rows * d[2]) m)")

# ==============================================================================
# 5. Save imaging artifacts
# ==============================================================================

println("Saving muted RTM image to JLD2...")
jldsave("outputs/data/rtm_basic_image_water_mute.jld2";
    rtm_image_raw=rtm_image_raw,
    rtm_image_muted=rtm_image_muted,
    model_true=m_true,
    model_mig=m_mig,
    n=n,
    d=d,
    o=o,
    nsrc=nsrc,
    nrec=nrec,
    source_depth=source_depth,
    receiver_depth=receiver_depth,
    recording_time=recording_time,
    dt=dt,
    f0=f0,
    water_mute_depth_m=water_mute_depth_m,
    mute_rows=mute_rows)

# ==============================================================================
# 6. Plot improved RTM image
# ==============================================================================

println("Creating muted RTM figure...")

x_min = o[1] / 1000f0
x_max = (o[1] + (n[1] - 1) * d[1]) / 1000f0
z_min = o[2] / 1000f0
z_max = (o[2] + (n[2] - 1) * d[2]) / 1000f0

rtm_display = adjoint(rtm_image_muted)
abs_max = maximum(abs.(rtm_display))
clip_level = 0.045f0
vmax = max(clip_level * abs_max, eps(Float32))

fig = figure(figsize=(8.4, 6.2))
imshow(rtm_display,
       cmap="gray",
       aspect="auto",
       vmin=-vmax,
       vmax=vmax,
       extent=[x_min, x_max, z_max, z_min])

xlabel("Lateral position (km)", fontsize=13)
ylabel("Depth (km)", fontsize=13)
title("Basic RTM Image (Water-Column Muted)", fontsize=18, pad=14)
tight_layout()
savefig("outputs/figures/rtm_basic_image_water_mute.png", dpi=360, bbox_inches="tight", pad_inches=0.12)
close(fig)

println("="^50)
println("IMPROVED RTM BENCHMARK COMPLETE")
println("Main artifacts saved:")
println("  - outputs/figures/rtm_basic_image_water_mute.png")
println("  - outputs/data/rtm_basic_image_water_mute.jld2")
println("Original RTM artifact preserved in-memory and saved alongside muted image")
println("Raw RTM image range: [$(minimum(rtm_image_raw)), $(maximum(rtm_image_raw))]")
println("Muted RTM image range: [$(minimum(rtm_image_muted)), $(maximum(rtm_image_muted))]")
println("="^50)
