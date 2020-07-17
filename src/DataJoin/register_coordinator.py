import logging
import os
import grpc
from DataJoin.common import coordinator_data_pb2
from DataJoin.common import coordinator_data_pb2_grpc
import time

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    import argparse

    parser = argparse.ArgumentParser(description='Start Register Worker UUId ....')
    parser.add_argument('coordinator_address', type=str,
                        help='address of coordinator service')
    parser.add_argument('coordinator_port', type=int,
                        help='the port of coordinator service')
    args = parser.parse_args()
    coordinator_address = args.coordinator_address
    coordinator_port = args.coordinator_port
    assert coordinator_address and coordinator_port, "coord address or coord port is None"
    coord_channel = grpc.insecure_channel('{}:{}'.format(coordinator_address, str(coordinator_port)))
    coord_stub = coordinator_data_pb2_grpc.PairServiceStub(coord_channel)
    remote_ip = None
    host_ip = None
    while not remote_ip:
        remote_ip = os.environ.get("REMOTE_IP", None)
    while not host_ip:
        host_ip = os.environ.get("HOST_IP", None)
    while remote_ip and host_ip:
        ip_port = "{0}:{1}".format(host_ip, os.environ.get("PORT0", None))
        request = coordinator_data_pb2.Request(ip_port=ip_port)
        request.uuid.append(remote_ip)
        print(11111111111, request)
        res_status = coord_stub.RegisterUUID(request)
        logging.info('Register Coordinator status: {0}'.format(res_status.status))
        if res_status.status:
            raise Exception("register coordinator: <%s> fail !" % res_status.err_msg)
        while not res_status.status:
            pair_service_info_response = coord_stub.GetPairInfo(request)
            logging.info('received GetPairInfo status: {}'.format(pair_service_info_response.status))
            status = pair_service_info_response.status
            status_code = status.status
            if status_code:
                time.sleep(2)
                continue
            else:
                service_pair = pair_service_info_response.service_map
                local_uuid = (service_pair[0]).local_uuid
                remote_uuid = (service_pair[0]).remote_uuid
                logging.info("query coordinator info success,local_uuid:{0},"
                             "remote_uuid:{1}".format(local_uuid, remote_uuid))
                break
        break
