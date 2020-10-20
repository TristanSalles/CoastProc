!!~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~!!
!!                                                                                   !!
!!  This file forms part of the Badlands surface processes modelling application.    !!
!!                                                                                   !!
!!  For full license and copyright information, please refer to the LICENSE.md file  !!
!!  located at the project root, or contact the authors.                             !!
!!                                                                                   !!
!!~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~!!

! Loop over node coordinates and find if they belong to local partition.
!
! f2py3 -c -m ocean ocean.f90

module ocean

  implicit none

  real(kind=8), parameter::pi        = 3.1415926535897931_8
  real(kind=8), parameter::onpi      = 1.0_8/3.1415926535897931_8
  real(kind=8), parameter::pi2       = pi*2.0_8
  real(kind=8), parameter::pion2     = pi*0.5_8
  real(kind=8), parameter::onpi2     =1.0_8/pi2
  real(kind=8), parameter::grav    = 9.81_8

contains

  subroutine airymodel(dx,dd,h0,depth,src,inland,shadow,c,l,travel,waveH,numrow,numcol)

    integer :: numrow,numcol
    integer,intent(in) :: shadow
    integer,intent(in) :: inland(numrow,numcol)

    real(kind=8),intent(in) :: dx
    real(kind=8),intent(in) :: dd
    real(kind=8),intent(in) :: h0
    real(kind=8),intent(in) :: depth(numrow,numcol)
    real(kind=8),intent(in) :: src(numrow,numcol)

    real(kind=8),intent(out) :: c(numrow,numcol)
    real(kind=8),intent(out) ::  l(numrow,numcol)
    real(kind=8),intent(out) ::  travel(numrow,numcol)
    real(kind=8),intent(out) ::  waveH(numrow,numcol)

    integer :: i, j, keeploop, ix, jx, k

    real(kind=8) :: TM, MN, l0, f0, k0, dt, tperiod0
    real(kind=8) :: cg0, c0, kh, tmp, frac, n
    real(kind=8) :: ks(numrow,numcol)

    integer,dimension(20)::iradius=(/-2,-1,1,2,-2,-1,0,1,2,-1,0,1,-2,-1,0,1,2,-1,0,-1/)
    integer,dimension(20)::jradius=(/ 0,0,0,0,1,1,1,1,1, 2,2,2,-1,-1,-1,-1,-1,-2,-2,-2/)

    real(kind=8),dimension(20)::dist=(/2.,1.,1.,2.,sqrt(5.),sqrt(2.),1., &
        sqrt(2.),sqrt(5.),sqrt(5.),2.,sqrt(5.),sqrt(5.),sqrt(2.), &
        1.,sqrt(2.),sqrt(5.),sqrt(5.),2.,sqrt(5.)/)

    c = 0.
    ks = 1.
    waveH = 0.

    ! calculate wave length (deep water)
    tperiod0 = max(0.47*h0+6.76, pi*pi*sqrt(h0/grav))

    l0=grav*tperiod0**2*onpi2
    f0=pi2/tperiod0
    k0=pi2/l0
    ! airy wave theory, deep water phase speed
    cg0=0.5_8*sqrt(grav/k0)  ! group speed
    c0=grav*tperiod0*onpi2

    ! set the step size
    l=l0
    do j = 1, numcol
      do i = 1, numrow
        ! conct contains all areas not in the shadow of land
        ! if areas are "exposed and in deep water, give them the "open water" conditions
        TM=l0
        if(inland(i,j)==0)then
          do
            MN=0.5_8*(l(i,j)+TM)
            TM=l(i,j)
            l(i,j)=l0*tanh(pi2*depth(i,j)/MN)
            if(abs(l(i,j)-TM)<1.0e-8_8)exit
          enddo
          c(i,j)=c0*l(i,j)/l0
          kh = depth(i,j)*pi2/l(i,j)
          tmp = 1.+2.*kh/sinh(2.*kh)
          waveH(i,j) = h0/sqrt(tanh(kh)*tmp)
          n = 0.5*tmp
          ks(i,j) = sqrt(c0/(2.*n*c(i,j)))
        endif
      end do
    end do

    ! Assign source points
    travel = src

    ! Perform Huygen's principle to find travel time and wave front
    keeploop = 1
    do
        keeploop = 0
        do j = 1, numcol
          do i = 1, numrow
              if(travel(i,j)>=0)then
                  do k = 1, 20
                      ix = i+iradius(k)
                      jx = j+jradius(k)
                      if(ix>0 .and. ix<=numrow .and. jx>0 .and. jx<=numcol)then
                          if(inland(ix,jx)==1)then
                              travel(ix,jx)=-1
                          else if(travel(ix,jx)<0)then
                              travel(ix,jx) = travel(i,j)+dist(k)*dx/c(i,j)
                              keeploop = 1
                              if(depth(i,j)/l(i,j)<0.5)then
                                  frac = 2.*(1.-dd)*depth(i,j)/l(i,j)+dd
                                  if(waveH(ix,jx)>frac*waveH(i,j)) waveH(ix,jx)=frac*waveH(i,j)
                              else
                                  if(shadow==1 .and. waveH(ix,jx)>waveH(i,j)) waveH(ix,jx)=waveH(i,j)
                              endif
                          else
                              dt = travel(i,j)+dist(k)*dx/c(i,j)
                              if(travel(ix,jx)>dt .and. dt>0)then
                                  travel(ix,jx) = dt
                                  if(depth(i,j)/l(i,j)<0.5)then
                                      frac = 2.*(1.-dd)*depth(i,j)/l(i,j)+dd
                                      if(waveH(ix,jx)>frac*waveH(i,j)) waveH(ix,jx)=frac*waveH(i,j)
                                  else
                                      if(shadow==1 .and. waveH(ix,jx)>waveH(i,j)) waveH(ix,jx)=waveH(i,j)
                                  endif
                                  keeploop = 1
                              endif
                          endif
                      endif
                  end do
              endif
          end do
        end do
        if(keeploop == 0)exit
    end do
    waveH = waveH * ks

    return

  end subroutine airymodel

  subroutine transport(iter,depth,hent,transX,transY,dz,dist,numrow,numcol)

    integer :: numrow,numcol

    integer,intent(in) :: iter
    real(kind=8),intent(in) :: depth(numrow,numcol)
    real(kind=8),intent(in) :: hent(numrow,numcol)
    real(kind=8),intent(in) :: transX(numrow,numcol)
    real(kind=8),intent(in) :: transY(numrow,numcol)

    real(kind=8),intent(out) :: dz(numrow,numcol)
    real(kind=8),intent(out) :: dist(numrow,numcol)

    integer :: i, j, k, loop, it, steps

    real(kind=8) :: ent(numrow,numcol),ndepth(numrow,numcol)

    dz = 0.
    steps = 20
    ndepth = depth+hent

    do k = 1, steps
      ent = hent/steps
      loop = 0
      it = 0
      do while(loop==0 .and. it<iter)
        loop = 1
        it = it+1
        do j = 2, numcol-1
          do i = 2, numrow-1
            if(ent(i,j)>0.)then
              loop = 0
              ! Below critical shear stress for entrainment deposit everything
              if(hent(i,j)==0.)then
                dz(i,j) = dz(i,j)+ent(i,j)
                ndepth(i,j) = ndepth(i,j)-ent(i,j)
              else
                ! Along the X-axis

                ! Moving towards East
                if(transX(i,j)>0)then
                  ! Inland deposit inside cell
                  if(ndepth(i+1,j)<=0)then
                    dz(i,j) = dz(i,j)+transX(i,j)*ent(i,j)
                    ndepth(i,j) = ndepth(i,j)-transX(i,j)*ent(i,j)
                  ! Transfert entrained sediment to neighbouring cell
                  else
                    ! In case the directions are following the same trend
                    if(transX(i+1,j)>=0)then
                      ent(i+1,j) = ent(i+1,j)+transX(i,j)*ent(i,j)
                    ! In case the directions are facing each others
                    else
                      dz(i,j) = dz(i,j)+0.5*transX(i,j)*ent(i,j)
                      ndepth(i,j) = ndepth(i,j)-0.5*transX(i,j)*ent(i,j)
                      dz(i+1,j) = dz(i+1,j)+0.5*transX(i,j)*ent(i,j)
                      ndepth(i+1,j) = ndepth(i+1,j)-0.5*transX(i,j)*ent(i,j)
                    endif
                  endif
                ! Moving towards West
                elseif(transX(i,j)<0)then
                  ! Inland deposit inside cell
                  if(ndepth(i-1,j)<=0)then
                    dz(i,j) = dz(i,j)-transX(i,j)*ent(i,j)
                    ndepth(i,j) = ndepth(i,j)+transX(i,j)*ent(i,j)
                  ! Transfert entrained sediment to neighbouring cell
                  else
                    ! In case the directions are following the same trend
                    if(transX(i-1,j)<=0)then
                      ent(i-1,j) = ent(i-1,j)-transX(i,j)*ent(i,j)
                    ! In case the directions are facing each others
                    else
                      dz(i,j) = dz(i,j)-0.5*transX(i,j)*ent(i,j)
                      ndepth(i,j) = ndepth(i,j)+0.5*transX(i,j)*ent(i,j)
                      dz(i-1,j) = dz(i-1,j)-0.5*transX(i,j)*ent(i,j)
                      ndepth(i-1,j) = ndepth(i-1,j)+0.5*transX(i,j)*ent(i,j)
                    endif
                  endif
                endif

                ! Along the Y-axis

                ! Moving towards North
                if(transY(i,j)>0)then
                  ! Inland deposit inside cell
                  if(ndepth(i,j+1)<=0)then
                    dz(i,j) = dz(i,j)+transY(i,j)*ent(i,j)
                    ndepth(i,j) = ndepth(i,j)-transY(i,j)*ent(i,j)
                  ! Transfert entrained sediment to neighbouring cell
                  else
                    ! In case the directions are following the same trend
                    if(transY(i,j+1)>=0)then
                      ent(i,j+1) = ent(i,j+1)+transY(i,j)*ent(i,j)
                    ! In case the directions are facing each others
                    else
                      dz(i,j) = dz(i,j)+0.5*transY(i,j)*ent(i,j)
                      ndepth(i,j) = ndepth(i,j)-0.5*transY(i,j)*ent(i,j)
                      dz(i,j+1) = dz(i,j+1)+0.5*transY(i,j)*ent(i,j)
                      ndepth(i,j+1) = ndepth(i,j+1)-0.5*transY(i,j)*ent(i,j)
                    endif
                  endif
                ! Moving towards South
                elseif(transY(i,j)<0)then
                  ! Inland deposit inside cell
                  if(ndepth(i,j-1)<=0)then
                    dz(i,j) = dz(i,j)-transY(i,j)*ent(i,j)
                    ndepth(i,j) = ndepth(i,j)+transY(i,j)*ent(i,j)
                  ! Transfert entrained sediment to neighbouring cell
                  else
                    ! In case the directions are following the same trend
                    if(transY(i,j-1)<=0)then
                      ent(i,j-1) = ent(i,j-1)-transY(i,j)*ent(i,j)
                    ! In case the directions are facing each others
                    else
                      dz(i,j) = dz(i,j)-0.5*transY(i,j)*ent(i,j)
                      ndepth(i,j) = ndepth(i,j)+0.5*transY(i,j)*ent(i,j)
                      dz(i,j-1) = dz(i,j-1)-0.5*transY(i,j)*ent(i,j)
                      ndepth(i,j-1) = ndepth(i,j-1)+0.5*transY(i,j)*ent(i,j)
                    endif
                  endif

                endif
              endif
              ent(i,j) = 0.
            endif
          enddo
        enddo
      enddo
      if(it>=1000)then
        dz = dz+ent
        ndepth = ndepth-ent
      endif
    enddo

    ! Find reworked sediment above water level
    dist = 0.
    do j = 1, numcol
      do i = 1, numrow
        if(dz(i,j)>depth(i,j)+hent(i,j).and.depth(i,j)+hent(i,j)>0.)then
          dist(i,j) = dz(i,j)-depth(i,j)-hent(i,j)
          dz(i,j) = depth(i,j)+hent(i,j)
        endif
      enddo
    enddo

    return

  end subroutine transport

  subroutine diffusion(oelev,dz,coeff,maxth,tstep,nstep,depo,numrow,numcol)

    integer :: numrow,numcol

    integer,intent(in) :: nstep
    real(kind=8),intent(in) :: maxth
    real(kind=8),intent(in) :: tstep
    real(kind=8),intent(in) :: oelev(numrow,numcol)
    real(kind=8),intent(in) :: dz(numrow,numcol)
    real(kind=8),intent(in) :: coeff


    real(kind=8),intent(out) :: depo(numrow,numcol)

    integer :: i,j,i1,j1,k,it
    real(kind=8) :: diffmarine(numrow,numcol),elev(numrow,numcol)

    integer,dimension(4)::is=(/1,0,-1,0/)
    integer,dimension(4)::js=(/0,1,0,-1/)
    real(kind=8) :: flx,mindt

    depo = dz
    elev = oelev

    do it=1,nstep
      diffmarine = 0.
      mindt = tstep
      do j = 2, numcol-1
        do i = 2, numrow-1
          do k = 1,4
            i1 = i+is(k)
            j1 = j+js(k)
            flx = elev(i1,j1)-elev(i,j)
            if(depo(i,j)>maxth .and. elev(i,j)>elev(i1,j1))then
              diffmarine(i,j) = diffmarine(i,j) + flx*coeff
            elseif(depo(i1,j1)>maxth .and. elev(i,j)<elev(i1,j1))then
              diffmarine(i,j) = diffmarine(i,j) + flx*coeff
            endif
          enddo
          if(diffmarine(i,j)<0. .and. diffmarine(i,j)*tstep<-depo(i,j))then
            mindt = min(-depo(i,j)/diffmarine(i,j),mindt)
          endif
        enddo
      enddo
      depo = depo + diffmarine*mindt
      elev = elev + diffmarine*mindt
    enddo

    return

  end subroutine diffusion

end module ocean
