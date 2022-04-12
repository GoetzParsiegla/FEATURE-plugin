library(MASS)

predictSites <- function(dat, precision=c("95", "99"), cutoff=0, refine.radius) {
  # Wrapper function for getSites. Returns an array of predicted sites
  #
  # Args:
  #   dat: An array, where the first column is the FEATURE scores, the second to 4th 
  #        columns are the xyz coordinates
  #   precision: An option to choose the cutoff based on benchmarked precision values
  #   cutoff: The score cutoff used to determine the retained points from dat.
  #
  # Returns:
  #   An array of predicted sites. 
  prec <- try(match.arg(precision), silent=TRUE)
  if (!is(prec, "try-error")) {  
    score.cuts <- c(2.08, 25.67)
    names(score.cuts) <- c("95", "99")
    cutoff <- score.cuts[prec]
  }
  
  dat <- dat[which(dat$scores >= cutoff),]
  pred <- getSites(dat, refine.radius)
  return(pred)
}


getSites <- function(dat, refine.radius) {
  # A recursive function that gets predicted sites from dat
  #
  # Args:
  #   dat: An array, where the first column is the FEATURE scores, the second to 4th 
  #        columns are the xyz coordinates
  #   sites: The current array of predicted sites
  #
  # Returns:
  #   An array of predicted sites. 
  if (dim(dat)[1] == 0) {
    return()
  } else {
    dat <- dat[order(dat$scores, decreasing = TRUE),] 
    site <- refineSite(dat, refine.radius)
    # Remove all points within 3.5A from site
    distToSite <- proxy::dist(site, dat[,2:4])
    ind <- which(distToSite <= 3.5)
    site <- c(site, length(ind), summary(dat[ind, 1]))
    dat <- dat[-ind,]
    return(rbind(site, getSites(dat, refine.radius)))
  }
}

refineSite <- function(dat, refine.radius) {
  # Takes the top scoring point in dat and returns a refined predicted site
  #
  # Args:
  #   dat: An array, where the first column is the FEATURE scores, the second to 4th 
  #        columns are the xyz coordinates
  #
  # Returns:
  #   A predicted site. 
  if (dim(dat)[1] == 1) {
    return(dat[,2:4])
  }
  ini.guess <- dat[1, 2:4]
  distToSite <- proxy::dist(ini.guess, dat[,2:4])
  indWithin <- which(distToSite <= refine.radius)
  site <- rbind(rep(0, 3))
  for (i in 1:3) {
    site[i] <- weighted.mean(dat[indWithin, (i+1)], exp(dat[indWithin, 1])) 
  }
  return(site)
}

