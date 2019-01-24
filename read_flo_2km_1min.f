      program read_flow
      integer nx,ny
      character*4 tag
      real u,v,c1,c2,c3,c4
C      integer iu,iv
C change u,v to real on 24 Apr 17
      real iu,iv
      open(2,file='in.flo',access='direct',recl=4)
      open(3,file='u.out',access='direct',recl=4)
      open(4,file='v.out',access='direct',recl=4)
      read(2,rec=1)tag
      read(2,rec=2)nx
      read(2,rec=3)ny
      print*,'tag=',tag
      print*,'nx=',nx
      print*,'ny=',ny
      irec=4
      irec2=1
      do j=1,ny
      do i=1,nx
      read(2,rec=irec)u
      irec=irec+1
      read(2,rec=irec)v
c convert displacement to velocity
c assume displacement in km/min, convert to m/s
c valid for using 1km data every minute
c             and 0.5km data every 30 sec
c x1000/60=16.667
c      iu=NINT(u*16.667)
c      iv=-(NINT(v*16.667))
c Conversion table:
c for displacements of 1 grid pt
c 1km/min: 1km/min =16.67 m/s
c1 0.5km/0.5min: 1km/min =16.667 m/s
c2 0.5km/1min: 0.5km/min = 8.333m/s
c3 0.5km/2min: 0.25km/min =4.167m/s
c4 0.5km/3min: 0.167km/min =2.783m/s
c5 2.0km/5min: 0.4km/min = 6.666m/s
c6 2.0km/1min: 2.0km/min=33.33m/s
c7 2.0km/10min: 0.2km/min=3.33m/s
      c1=16.667
      c2=8.333
      c3=4.167
      c4=2.783
      c5=6.666
      c6=33.33
      c7=3.33
c use c6 here
      iu=(u*c6)
      iv=-(v*c6)

c      if(iu.ne.0)then
c      print*,'iu=',iu
c      endif
c      if(iv.ne.0)then
c      print*,'iv=',iv
c      endif

      write(3,rec=irec2)iu
      write(4,rec=irec2)iv
      nrec2=irec2
      nrec=irec
      irec=irec+1
      irec2=irec2+1
      enddo
      enddo
      print*,'nrec=',nrec
      print*,'nrec2=',nrec2
      return
      end


