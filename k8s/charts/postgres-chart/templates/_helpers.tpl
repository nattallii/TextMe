{{- define "postgres-chart.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "postgres-chart.fullname" -}}
{{- .Release.Name }}-{{ .Chart.Name }}
{{- end -}}