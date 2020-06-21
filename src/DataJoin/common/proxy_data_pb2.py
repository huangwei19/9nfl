# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: DataJoin/common/proxy_data.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='DataJoin/common/proxy_data.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n DataJoin/common/proxy_data.proto\"4\n\x04\x44\x61ta\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x0c\x12\x10\n\x08operator\x18\x03 \x01(\t\"\x1e\n\nHeaderData\x12\x10\n\x08operator\x18\x01 \x01(\t\":\n\x06Packet\x12\x1b\n\x06header\x18\x01 \x01(\x0b\x32\x0b.HeaderData\x12\x13\n\x04\x62ody\x18\x02 \x01(\x0b\x32\x05.Data21\n\x10ProxyDataService\x12\x1d\n\tUnaryCall\x12\x07.Packet\x1a\x07.Packetb\x06proto3')
)




_DATA = _descriptor.Descriptor(
  name='Data',
  full_name='Data',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='Data.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='Data.value', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='operator', full_name='Data.operator', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=36,
  serialized_end=88,
)


_HEADERDATA = _descriptor.Descriptor(
  name='HeaderData',
  full_name='HeaderData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='operator', full_name='HeaderData.operator', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=90,
  serialized_end=120,
)


_PACKET = _descriptor.Descriptor(
  name='Packet',
  full_name='Packet',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='Packet.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='body', full_name='Packet.body', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=122,
  serialized_end=180,
)

_PACKET.fields_by_name['header'].message_type = _HEADERDATA
_PACKET.fields_by_name['body'].message_type = _DATA
DESCRIPTOR.message_types_by_name['Data'] = _DATA
DESCRIPTOR.message_types_by_name['HeaderData'] = _HEADERDATA
DESCRIPTOR.message_types_by_name['Packet'] = _PACKET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Data = _reflection.GeneratedProtocolMessageType('Data', (_message.Message,), {
  'DESCRIPTOR' : _DATA,
  '__module__' : 'DataJoin.common.proxy_data_pb2'
  # @@protoc_insertion_point(class_scope:Data)
  })
_sym_db.RegisterMessage(Data)

HeaderData = _reflection.GeneratedProtocolMessageType('HeaderData', (_message.Message,), {
  'DESCRIPTOR' : _HEADERDATA,
  '__module__' : 'DataJoin.common.proxy_data_pb2'
  # @@protoc_insertion_point(class_scope:HeaderData)
  })
_sym_db.RegisterMessage(HeaderData)

Packet = _reflection.GeneratedProtocolMessageType('Packet', (_message.Message,), {
  'DESCRIPTOR' : _PACKET,
  '__module__' : 'DataJoin.common.proxy_data_pb2'
  # @@protoc_insertion_point(class_scope:Packet)
  })
_sym_db.RegisterMessage(Packet)



_PROXYDATASERVICE = _descriptor.ServiceDescriptor(
  name='ProxyDataService',
  full_name='ProxyDataService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=182,
  serialized_end=231,
  methods=[
  _descriptor.MethodDescriptor(
    name='UnaryCall',
    full_name='ProxyDataService.UnaryCall',
    index=0,
    containing_service=None,
    input_type=_PACKET,
    output_type=_PACKET,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PROXYDATASERVICE)

DESCRIPTOR.services_by_name['ProxyDataService'] = _PROXYDATASERVICE

# @@protoc_insertion_point(module_scope)
