#' a convenience function to install a package if it isn't already
#'
#' @export
load_install <- function(pkg){
  if(!require(pkg, character.only = T)){
    install.packages(pkg)
    library(pkg, character.only = T)
  }
}