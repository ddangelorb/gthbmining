library("vioplot")
library("beanplot")
library("ggplot2")
library("car")
library("effsize")

setwd("/Users/danieldangeloresendebarros/Projects/sdp4ossp/returninfo/r")
data_metrics<-read.csv("results_data_final.csv", sep=",")

#### exploratory analysis

# grouped boxplot
ggplot(data_metrics, aes(x=performance, y=releases, fill=time)) +
  geom_boxplot()

#subsetting each metric

low_before <- data_metrics[ which(data_metrics$performance=='Low Performers' & data_metrics$time=='Before CI/CD'), ]
low_after <- data_metrics[ which(data_metrics$performance=='Low Performers' & data_metrics$time=='With CI/CD'), ]

medium_before <- data_metrics[ which(data_metrics$performance=='Medium Performers' & data_metrics$time=='Before CI/CD'), ]
medium_after <- data_metrics[ which(data_metrics$performance=='Medium Performers' & data_metrics$time=='With CI/CD'), ]

#### total_controller_error

shapiro.test(low_before$releases)
#plot(density(low_before$releases))

shapiro.test(low_after$releases)

shapiro.test(medium_before$releases)
#plot(density(medium_before$releases))

shapiro.test(medium_after$releases)
#Para rejeitarmos a hip??tese nula, o valor de p deve ser inferior a 0.05 (p < 0.05). Neste exemplo, vamos observar que o valor ?? 0.46, indicando que os dados seguem uma distribui????o normal. 

wilcox.test(low_before$releases,low_after$releases, paired = TRUE)

wilcox.test(medium_before$releases,medium_after$releases, paired = TRUE)

#effect size
cliff.delta(low_before$releases,low_after$releases)

cliff.delta(medium_before$releases,medium_after$releases)