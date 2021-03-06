#' Uh and Um data from the PNC
#' @format a data frame with 22 columns. Speech chunks were defined by 
#' continuous speech bordered on each side by a pause of 200 miliseconds or more
#'  \describe{
#'    \item{idstring}{Unique id string for each speaker}
#'    \item{word}{\code{UM}, \code{UH}, \code{AND_UH}, \code{AND_UM}, or \code{UM_UH}}
#'    \item{start_time}{Onset time of filled pause, in seconds}
#'    \item{end_time}{Offset time of filled pause, in seconds}
#'    \item{vowel_start}{Onset time of filled pause vowel}
#'    \item{vowel_end}{Offset time of filled pause vowel}
#'    \item{nasal_start}{Onset time of nasal, if \code{UM}}
#'    \item{nasal_end}{Offset time of nasal, if \code{UM}}
#'    \item{next_seg}{The next segment on the phone tier}
#'    \item{next_seg_start}{Start time of next segment}
#'    \item{next_seg_end}{End time of next segment}
#'    \item{chunk_start}{Onset time of speech chunk}
#'    \item{chunk_end}{Offset time of speech chunk}
#'    \item{nwords}{Total number of words from this speaker}
#'    \item{sex}{Sex of speaker}
#'    \item{year}{Year of interview}
#'    \item{age}{Age of speaker at time of interview}
#'    \item{ethnicity}{A number of single character codes for speakers' ethnicity}
#'    \item{schooling}{Number of years of schooling}
#'    \item{transcribed}{Total number of transcribed seconds of interview}
#'    \item{total}{Total length of recording}
#'    \item{nvowels}{Number of measured stressed vowels (irrelevant to UM/UH)}
#'  }
#'  
#' @source Philadelphia Neighborhood Corpus
"um_PNC"
