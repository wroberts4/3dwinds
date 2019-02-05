from main import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area
speed, angle = calculate_velocity('/Users/wroberts/Documents/3dwinds/airs1.flo', i=0, j=0, lat_0=60, lon_0=0,
                                  pixel_size=4000, center=(90, 0))
print(speed)
