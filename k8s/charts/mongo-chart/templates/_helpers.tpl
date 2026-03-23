{{- define "mongo-chart.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "mongo-chart.fullname" -}}
{{- .Release.Name }}-{{ .Chart.Name }}
{{- end -}}