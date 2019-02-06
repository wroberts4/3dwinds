from main import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area
speed, angle = calculate_velocity(60, 0, 'C:/Users/William/Documents/3dwinds/airs1.flo', i=0, j=0,
                                  pixel_size=4000, center=(90, 0))
print(speed)
