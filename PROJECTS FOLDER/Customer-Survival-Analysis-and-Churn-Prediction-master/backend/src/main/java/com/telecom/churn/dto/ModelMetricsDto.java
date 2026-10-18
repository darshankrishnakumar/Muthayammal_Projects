package com.telecom.churn.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ModelMetricsDto {

    private String model;
    private String datasetSource;
    private Integer trainRecordCount;
    private Integer testRecordCount;
    private Integer totalRecordCount;
    private Double accuracy;
    private Double precision;
    private Double recall;
    private Double f1Score;
    private Double rocAuc;
    private Map<String, Integer> confusionMatrix;
    private List<String> featureNames;

    public ModelMetricsDto() {}

    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }

    public String getDatasetSource() { return datasetSource; }
    public void setDatasetSource(String datasetSource) { this.datasetSource = datasetSource; }

    public Integer getTrainRecordCount() { return trainRecordCount; }
    public void setTrainRecordCount(Integer trainRecordCount) { this.trainRecordCount = trainRecordCount; }

    public Integer getTestRecordCount() { return testRecordCount; }
    public void setTestRecordCount(Integer testRecordCount) { this.testRecordCount = testRecordCount; }

    public Integer getTotalRecordCount() { return totalRecordCount; }
    public void setTotalRecordCount(Integer totalRecordCount) { this.totalRecordCount = totalRecordCount; }

    public Double getAccuracy() { return accuracy; }
    public void setAccuracy(Double accuracy) { this.accuracy = accuracy; }

    public Double getPrecision() { return precision; }
    public void setPrecision(Double precision) { this.precision = precision; }

    public Double getRecall() { return recall; }
    public void setRecall(Double recall) { this.recall = recall; }

    public Double getF1Score() { return f1Score; }
    public void setF1Score(Double f1Score) { this.f1Score = f1Score; }

    public Double getRocAuc() { return rocAuc; }
    public void setRocAuc(Double rocAuc) { this.rocAuc = rocAuc; }

    public Map<String, Integer> getConfusionMatrix() { return confusionMatrix; }
    public void setConfusionMatrix(Map<String, Integer> confusionMatrix) { this.confusionMatrix = confusionMatrix; }

    public List<String> getFeatureNames() { return featureNames; }
    public void setFeatureNames(List<String> featureNames) { this.featureNames = featureNames; }
}
