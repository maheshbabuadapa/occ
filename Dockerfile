FROM nginx:latest
VOLUME [ "/usr/share/nginx/html/" ]
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
