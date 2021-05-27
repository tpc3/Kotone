FROM archlinux:base-devel
WORKDIR /opt/Kotone
COPY . .
RUN /opt/Kotone/docker-build.sh
CMD python /opt/Kotone/main.py
