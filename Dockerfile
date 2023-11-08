FROM nginx
COPY ./web/index.html /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/default.conf
COPY ./web/nginx.conf /etc/nginx/conf.d
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]