{{- define "infra-chart.rabbitmq.fullname" -}}
{{ .Release.Name }}-rabbitmq
{{- end }}

{{- define "infra-chart.redis.fullname" -}}
{{ .Release.Name }}-redis
{{- end }}

{{- define "infra-chart.minio.fullname" -}}
{{ .Release.Name }}-minio
{{- end }}