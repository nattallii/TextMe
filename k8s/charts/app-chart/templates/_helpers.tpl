{{- define "app-chart.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "app-chart.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}