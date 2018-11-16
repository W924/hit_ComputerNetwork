/*
* THIS FILE IS FOR IP FORWARD TEST
*/
#include "sysInclude.h"
#include <vector>

// system support
extern void fwd_LocalRcv(char *pBuffer, int length);

extern void fwd_SendtoLower(char *pBuffer, int length, unsigned int nexthop);

extern void fwd_DiscardPkt(char *pBuffer, int type);

extern unsigned int getIpv4Address( );

// implemented by students

typedef struct route_node
{
	unsigned int dest;		// 目标地址
	unsigned int masklen;	// 掩码长度
	unsigned int nexthop;	// 下一条地址
}Node;

vector<Node> route_table;

short compute_checksum(char *pBuffer, int header_len) {
	int i, sum = 0;
	for(i = 0; i < header_len * 2; i++) {
		if(i != 5)
		{
			sum += (int)((unsigned char)pBuffer[i * 2] << 8);
			sum += (int)((unsigned char)pBuffer[i * 2 + 1]);
		}
	}
	while((sum & 0xffff0000) != 0) {
		sum = (sum & 0xffff) + ((sum >> 16) & 0xffff);
	}
	return (~sum) & 0xffff;
}

bool cmp(const Node & a, const Node & b) {
	if (htonl(a.dest) > htonl(b.dest)) {
		return true;
	}
	else if (htonl(a.dest) == htonl(b.dest)) {
		return htonl(a.masklen) > htonl(b.masklen);
	}
	else {
		return false;
	}
}

void stud_Route_Init()
{
	route_table.clear();
}

void stud_route_add(stud_route_msg *proute)
{
	Node *new_node = new Node();
	new_node->dest = ntohl(proute->dest);
	new_node->masklen = ntohl(proute->masklen);
	new_node->nexthop = ntohl(proute->nexthop);
	route_table.push_back(*new_node);
	sort(route_table.begin(), route_table.end(), cmp);
	return;
}

int stud_fwd_deal(char *pBuffer, int length)
{
	int version = 0xf0 & pBuffer[0];
	int header_len = 0xf & pBuffer[0];
	int ttl = (int)pBuffer[8];
	int dest_addr = ntohl(*(unsigned int *)(pBuffer + 16));  
	int local_addr = getIpv4Address();
	
	if (dest_addr == local_addr) {                                                             
		fwd_LocalRcv(pBuffer, length);
		return 0;
	}
	
	if (ttl <= 0) {
		fwd_DiscardPkt(pBuffer, STUD_FORWARD_TEST_TTLERROR);
		return 1;
	}
	
	vector<Node>::iterator ii = route_table.begin();
	for (; ii != route_table.end(); ii++) {
		if (ii->dest == dest_addr) {
			pBuffer[8]--;        
			*(short *)(pBuffer + 10) = htons(compute_checksum(pBuffer, 5));
			
			fwd_SendtoLower(pBuffer, length, ii->nexthop);         
			return 0;
		}
	}
	
	fwd_DiscardPkt(pBuffer, STUD_FORWARD_TEST_NOROUTE);       
	return 1;
}
