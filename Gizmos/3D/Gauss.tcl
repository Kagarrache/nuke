# Generate gaussian random (normal distribution)
proc gauss {seed} {
 set tempseed [expression random($seed)]
 set tempcdf [expression (-log(min($tempseed,1-$tempseed)))+0.4843]
 
 return [expression ($tempseed-0.5<0?-1:1)*($tempcdf-((2.515517+0.802853*$tempcdf+0.010328*pow($tempcdf,2))/((1+1.432788*$tempcdf+0.189269*pow($tempcdf,2)+0.001308*pow($tempcdf,3)))))*0.25]
}
